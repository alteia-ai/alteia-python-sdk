import concurrent.futures as cf
import logging
from threading import Lock
from typing import Callable
from urllib.parse import urljoin

import urllib3

from alteia.core.connection.abstract_connection import AbstractConnection

LOGGER = logging.getLogger(__name__)


def _load_url(http: urllib3.request.RequestMethods, cb: Callable = None, **params):
    response = http.request(**params)
    if cb is not None:
        cb(response)
    return response


class AsyncConnection(AbstractConnection):
    def __init__(self, *, base_url, disable_ssl_certificate,
                 token_manager, retries, max_requests_workers=6,
                 proxy_url=None):
        super().__init__(base_url=base_url,
                         disable_ssl_certificate=disable_ssl_certificate,
                         token_manager=token_manager, retries=retries)
        self._access_token_lock = Lock()
        self._executor = cf.ThreadPoolExecutor(max_workers=max_requests_workers)
        self._max_requests_workers = max_requests_workers
        manager_kw = {'cert_reqs': ('CERT_NONE' if disable_ssl_certificate
                                    else 'CERT_REQUIRED'),
                      'num_pools': max_requests_workers}
        pool_kw = {'maxsize': max_requests_workers,
                   'retries': retries,
                   'block': True}
        if proxy_url is not None:
            self._http = urllib3.ProxyManager(
                proxy_url=proxy_url, **manager_kw, **pool_kw)
        else:
            self._http = urllib3.PoolManager(**manager_kw, **pool_kw)

    @property
    def executor(self):
        return self._executor

    @property
    def max_request_workers(self):
        return self._max_requests_workers

    def _add_authorization_maybe(self, headers: dict, url: str):
        with self._access_token_lock:
            super()._add_authorization_maybe(headers, url)

    def post(self, path, headers=None, callback=None, data=None, timeout=None,
             retries=None):
        url = urljoin(self._base_url, path)
        params = {'method': 'POST',
                  'url': url,
                  'headers': headers,
                  'body': data or {},
                  'retries': retries or self._retries,
                  'timeout': timeout}
        return self._send_request(params, on_finish_callback=callback)

    def put(self, path, headers=None, callback=None, data=None, timeout=None,
            retries=None):
        url = urljoin(self._base_url, self._encode_spaces(path))
        params = {'method': 'PUT',
                  'url': url,
                  'headers': headers,
                  'body': data or {},
                  'retries': retries or self._retries,
                  'timeout': timeout}
        return self._send_request(params=params, on_finish_callback=callback)

    def _send_request(self, params, on_finish_callback):
        params['headers'] = params['headers'] or {}
        params['timeout'] = params['timeout'] or self.request_timeout
        self._add_authorization_maybe(params['headers'], params['url'])
        self._add_user_agent(params['headers'])
        try:
            token = params['headers']['Authorization'].split('Bearer')[1].strip()
        except KeyError:
            token = None

        def extended_callback(response, *args, **kwargs):
            if response.status == 401:
                LOGGER.debug('Got a 401 status')
                skip = self._skip_token_renewal(params['url'])
                if not skip:
                    with self._access_token_lock:  # block concurrent send requests
                        renewed = (token != self._token_manager.token.access_token)
                        if renewed:
                            LOGGER.debug('Token already renewed')
                        else:
                            self._renew_token()

            if on_finish_callback:
                on_finish_callback(response)

        LOGGER.debug(f"Making request {params['method']} to {params['url']}")
        return self._executor.submit(_load_url, self._http, extended_callback, **params)
