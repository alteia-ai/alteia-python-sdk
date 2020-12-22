"""Connection credentials.

"""

import base64


class Credentials():
    """Base class for connection credentials."""

    def __init__(self, client_id, secret, *, data, scope=None):
        self._data = data
        secret = '{}:{}'.format(client_id, secret)
        self._encoded_secret = base64.b64encode(secret.encode()).decode()

    @property
    def encoded_secret(self):
        return self._encoded_secret

    @property
    def data(self):
        return self._data


class ClientCredentials(Credentials):
    """Client credentials."""

    def __init__(self, client_id, secret, *, scope=None):
        data = {'grant_type': 'client_credentials'}

        if scope is not None:
            data['scope'] = scope

        super().__init__(client_id, secret, data=data)


class UserCredentials(Credentials):
    """User credentials."""

    __sdk_client_id = '0de76e3a-3960-48df-83cc-9d7dc9a90a7a'
    __secret = 'a13497e6-3dab-45b5-b43e-dbd9089faf6a'

    def __init__(self, user, password, *, client_id=None, secret=None, scope=None):
        client_id = client_id or self.__sdk_client_id
        secret = secret or self.__secret
        data = {'grant_type': 'password',
                'username': user,
                'password': password}

        if scope is not None:
            data['scope'] = scope

        super().__init__(client_id, secret, data=data)
