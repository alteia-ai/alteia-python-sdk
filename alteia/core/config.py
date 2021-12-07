"""Configuration helpers.

"""

import json
import logging
import os

from appdirs import user_data_dir

from alteia.core.utils.filehelper import read_file

LOGGER = logging.getLogger(__name__)

APPNAME = "alteia"
APPAUTHOR = "Alteia"
DEFAULT_CONF_DIR = user_data_dir(APPNAME, APPAUTHOR)
DEFAULT_URL = 'https://app.alteia.com'
DEFAULT_CONNECTION_CONF = {'disable_ssl_certificate': True}


class ConnectionConfig:
    """Connection configuration.

    """
    def __init__(self, file_path: str = None, *,
                 user: str = None, password: str = None,
                 client_id: str = None, client_secret: str = None,
                 url: str = None, domain: str = None, proxy_url: str = None,
                 access_token: str = None, **kwargs):
        """Initializes a connection configuration.

        Args:
            file_path: Optional path to a custom configuration file.

            user: Optional username (email).

            password: Optional password (mandatory if ``username`` is defined).

            client_id: Optional OAuth client identifier.

            client_secret: Optional OAuth client secret (mandatory if
                ``client_id`` is defined).

            url: Optional platform URL (default ``https://app.alteia.com``).

            domain: Optional domain.

            proxy_url: Optional proxy URL.

            access_token: Optional access token.

            kwargs: Optional keyword arguments to merge with
                            the configuration.

          kwargs : Optional arguments.

        Three sources of configuration are merged:

        - The optional arguments `kwargs`.

        - The file at path `file_path`.

        - The default configuration.

        The configuration file is expected to be written in JSON.

        """
        if file_path:
            LOGGER.info(f'Load custom configuration file from {file_path}')
            custom_conf = json.loads(read_file(file_path=file_path))
        else:
            user_conf_path = os.path.join(DEFAULT_CONF_DIR, 'config-connection.json')
            if os.path.exists(user_conf_path):
                LOGGER.info(f'Load user configuration file from {user_conf_path}')
                custom_conf = json.loads(read_file(file_path=user_conf_path))
            else:
                custom_conf = {}

        self.url = url or custom_conf.get('url') or DEFAULT_URL
        self.connection = custom_conf.get('connection') or DEFAULT_CONNECTION_CONF
        self.user = user or custom_conf.get('user')
        self.password = password or custom_conf.get('password')
        self.client_id = client_id or custom_conf.get('client_id')
        self.client_secret = client_secret or custom_conf.get('client_secret')
        self.domain = domain or custom_conf.get('domain')
        self.proxy_url = proxy_url or custom_conf.get('proxy_url')
        self.access_token = access_token or custom_conf.get('access_token')

        for name, val in kwargs.items():
            setattr(self, name, val)
