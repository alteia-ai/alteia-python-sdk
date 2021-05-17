import logging
import urllib.parse

import alteia

DEFAULT_REQUESTS_TIMEOUT = 30.0
LOGGER = logging.getLogger(__name__)


class AbstractConnection(object):
    request_timeout = DEFAULT_REQUESTS_TIMEOUT

    def __init__(self, *, base_url, disable_ssl_certificate, token_manager=None,
                 retries=None):
        self._disable_ssl_certificate = disable_ssl_certificate
        self._base_url = base_url[:-1] if base_url.endswith('/') else base_url
        self._token_manager = token_manager
        self._retries = retries
        self._user_agent = None
        self._netloc = urllib.parse.urlsplit(base_url).netloc

    def _renew_token(self):
        self._token_manager.renew_token()

    def _add_authorization_maybe(self, headers: dict, url: str):
        netloc = urllib.parse.urlsplit(url).netloc
        if netloc != self._netloc:
            LOGGER.info('No need for authorization header')
            return

        token = self._token_manager.token
        if token.token_type and token.access_token:
            auth = '{} {}'.format(token.token_type, token.access_token)
            headers['Authorization'] = auth
        elif 'Authorization' not in headers:
            LOGGER.warning('Authorization header not set')

    def _skip_token_renewal(self, url: str):
        parsed_url = urllib.parse.urlsplit(url)
        if parsed_url.netloc != self._netloc:
            return True

        if parsed_url.path == self._token_manager._path:
            return True         # escape from infinite recursions

        return False

    def _ensure_stream_rewind(self, params: dict):
        if 'body' in params and hasattr(params['body'], 'seek'):
            params['body_pos'] = 0

    def _add_user_agent(self, headers: dict):
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.user_agent

    def _add_referer(self, headers: dict):
        if 'referer' not in headers:
            headers['referer'] = self._base_url

    @property
    def user_agent(self):
        if not self._user_agent:
            self._user_agent = '{product}/{version}'.format(
                product='alteia-python-sdk',
                version=alteia.__version__)
        return self._user_agent

    @staticmethod
    def _encode_spaces(url):
        return url.replace(' ', '_')
