import collections
import json
import logging
import urllib.parse
from typing import Any, Dict, Optional

from alteia.core.errors import TokenRenewalError

LOGGER = logging.getLogger(__name__)

Token = collections.namedtuple('Token',
                               ('access_token', 'token_type',
                                'expires_in', 'refresh_token'))


class TokenManager():
    def __init__(self, *, connection, credentials,
                 access_token=None, token_type=None):
        self._connection = connection
        self._credentials = credentials
        self._token = Token(access_token, token_type, None, None)
        self._path = urllib.parse.urlsplit('/dxauth/oauth/token').path

    @property
    def credentials(self):
        return self._credentials

    @property
    def token(self):
        return self._token

    def renew_token(self):
        if not self._credentials:
            LOGGER.warning('Token renewal requires credentials ')
            return

        LOGGER.debug('Trying to get a new token...')
        self._token = Token(None, None, None, None)
        headers = {'Authorization':
                   'Basic {}'.format(self._credentials.encoded_secret),
                   'Content-Type': 'application/json'}
        data = json.dumps(self._credentials.data)
        decoded_data = self._connection.post(path=self._path,
                                             data=data,
                                             headers=headers,
                                             as_json=True)

        if 'access_token' in decoded_data:
            self._token = Token._make((decoded_data['access_token'],
                                       decoded_data['token_type'],
                                       decoded_data['expires_in'],
                                       decoded_data['refresh_token']))
            LOGGER.debug('Got a new token')
        else:
            LOGGER.error(f'Unsupported response: {decoded_data}')
            raise TokenRenewalError()

    def describe_token(self, token: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Describe an access token.

        Args:

            token: Optional token string (if missing, describe the current user token).

        Returns:
            token : Token description of the current SDK user.

        """
        params = kwargs
        if token:
            params['token'] = token
        return self._connection.post(
            path='/dxauth/describe-token',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(params),
            as_json=True
        )
