"""Connection credentials.

"""

import base64


class Credentials():
    """Base class for connection credentials."""

    def __init__(self, client_id, client_secret, *, data, **kwargs):
        self._data = data
        secret = f'{client_id}:{client_secret}'
        self._encoded_secret = base64.b64encode(secret.encode()).decode()

    @property
    def encoded_secret(self):
        return self._encoded_secret

    @property
    def data(self):
        return self._data


class ClientCredentials(Credentials):
    """Client credentials."""

    def __init__(self, client_id, client_secret, **kwargs):
        data = {'grant_type': 'client_credentials'}

        super().__init__(client_id, client_secret, data=data)


class UserCredentials(Credentials):
    """User credentials."""

    __sdk_client_id = '0de76e3a-3960-48df-83cc-9d7dc9a90a7a'
    __sdk_client_secret = 'a13497e6-3dab-45b5-b43e-dbd9089faf6a'

    def __init__(self, user, password, *,
                 client_id=None, client_secret=None, scope=None, **kwargs):
        client_id = client_id or self.__sdk_client_id
        client_secret = client_secret or self.__sdk_client_secret
        data = kwargs
        data.update({
            'grant_type': 'password',
            'username': user,
            'password': password
        })

        if scope is not None:
            data['scope'] = scope

        super().__init__(client_id, client_secret, data=data)
