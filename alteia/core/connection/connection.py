import json
import logging
from urllib.parse import urljoin

import urllib3
from urllib3.util.retry import Retry

from alteia.core.connection.abstract_connection import AbstractConnection
from alteia.core.connection.async_connection import AsyncConnection
from alteia.core.connection.token import TokenManager
from alteia.core.errors import ResponseError

LOGGER = logging.getLogger(__name__)


class Connection(AbstractConnection):
    def __init__(self, *, base_url, disable_ssl_certificate=False,
                 credentials=None, max_retries=10,
                 access_token=None, proxy_url=None):
        super().__init__(base_url=base_url,
                         disable_ssl_certificate=disable_ssl_certificate)

        cert_reqs = 'CERT_REQUIRED'
        if disable_ssl_certificate:
            cert_reqs = 'CERT_NONE'
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if proxy_url is not None:
            self._http = urllib3.ProxyManager(proxy_url=proxy_url,
                                              cert_reqs=cert_reqs)
        else:
            self._http = urllib3.PoolManager(cert_reqs=cert_reqs)

        self._retries = Retry(total=max_retries, backoff_factor=1,
                              status_forcelist=[409, 413, 429,
                                                500, 502, 503, 504],
                              allowed_methods=frozenset(
                                  ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS',
                                   'TRACE', 'POST']))

        token_type = 'Bearer' if access_token else None
        self._token_manager = TokenManager(connection=self,
                                           credentials=credentials,
                                           access_token=access_token,
                                           token_type=token_type)

        self._async_connection = AsyncConnection(
                base_url=base_url,
                disable_ssl_certificate=disable_ssl_certificate,
                token_manager=self._token_manager,
                retries=self._retries,
                proxy_url=proxy_url)

    @property
    def asynchronous(self):
        return self._async_connection

    def post(self, path, headers=None, data=None, timeout=None, as_json=False,
             preload_content=True, retries=None):
        """
            POST utility method
        """
        url = urljoin(self._base_url, path)
        params = {'url': url,
                  'body': data or {},
                  'headers': headers,
                  'method': 'POST',
                  'timeout': timeout,
                  'retries': retries or self._retries,
                  'preload_content': preload_content}
        resp = self._send_request(params)
        if as_json:
            return json.loads(resp.data.decode('utf-8'))
        if preload_content:
            return resp.data
        return resp

    def get(self, path, headers=None, timeout=None, as_json=False,
            preload_content=True, retries=None):
        """
             GET utility method
        """
        url = urljoin(self._base_url, path)
        params = {'url': url,
                  'headers': headers,
                  'method': 'GET',
                  'timeout': timeout,
                  'retries': retries or self._retries,
                  'preload_content': preload_content}
        resp = self._send_request(params)
        if as_json:
            return json.loads(resp.data.decode('utf-8'))
        if preload_content:
            return resp.data
        return resp

    def put(self, path, headers=None, data=None, timeout=None, as_json=False,
            preload_content=True, retries=None):
        """
            PUT utility method
        """
        url = urljoin(self._base_url, path)
        params = {'url': url,
                  'body': data or {},
                  'headers': headers,
                  'method': 'PUT',
                  'timeout': timeout,
                  'retries': retries or self._retries,
                  'preload_content': preload_content}
        resp = self._send_request(params)
        if as_json:
            return json.loads(resp.data.decode('utf-8'))
        if preload_content:
            return resp.data
        return resp

    def delete(self, path, headers=None, data=None, timeout=None,
               as_json=False, preload_content=True, retries=None):
        """
            DELETE utility method
        """
        url = urljoin(self._base_url, path)
        params = {'url': url,
                  'body': data or {},
                  'headers': headers,
                  'method': 'DELETE',
                  'timeout': timeout,
                  'retries': retries or self._retries}
        resp = self._send_request(params)
        if as_json:
            return json.loads(resp.data.decode('utf-8'))
        if preload_content:
            return resp.data
        return resp

    def _send_request(self, params):
        params['headers'] = params['headers'] or {}
        params['timeout'] = params['timeout'] or self.request_timeout
        self._add_authorization_maybe(params['headers'], params['url'])
        self._add_user_agent(params['headers'])
        self._add_referer(params['headers'])
        self._ensure_stream_rewind(params)

        LOGGER.debug(f'Making {params["method"]} request to {params["url"]}')

        response = self._http.request(**params)

        if response.status == 401:
            LOGGER.debug('Got a 401 status')
            skip = self._skip_token_renewal(params['url'])
            if not skip:
                self._renew_token()
                self._add_authorization_maybe(params['headers'], params['url'])

                LOGGER.debug('Retrying to request using the new token..')
                response = self._http.request(**params)

        if response.status not in range(200, 300):
            raise ResponseError('{status}: {message}'.format(
                status=response.status,
                message=response.data[:256]))

        return response
