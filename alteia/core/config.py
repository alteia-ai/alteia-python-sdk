"""Configuration helpers.

"""

import json
import logging
import os

from appdirs import user_data_dir

from alteia.core.utils.filehelper import read_file
from alteia.core.utils.utils import dict_merge

__all__ = ('Config', 'ConnectionConfig')

LOGGER = logging.getLogger(__name__)

APPNAME = "alteia"
APPAUTHOR = "Alteia"
DEFAULT_CONF_DIR = user_data_dir(APPNAME, APPAUTHOR)


class Config(object):
    """Base class handling configuration.

    It merges multiple sources of configuration and makes all
    configured properties available as instance attributes.

    Three sources of configuration are handled:

    - The optional arguments given as `kwargs`.

    - A custom configuration file.

    - A default configuration.

    """
    def __init__(self, defaults=None, custom=None, **kwargs):
        conf = defaults or {}
        conf = dict_merge(conf, custom or {})
        conf = dict_merge(conf, kwargs)

        for name, val in conf.items():
            setattr(self, name, val)


class ConnectionConfig(Config):
    """Connection configuration.

    """
    def __init__(self, file_path: str = None, *,
                 user: str = None, password: str = None,
                 client_id: str = None, secret: str = None,
                 url: str = None, domain: str = None, proxy_url: str = None,
                 **kwargs):
        """Initializes a connection configuration.

        Args:
            file_path: Optional path to a custom configuration file.

            user: Optional username (email).

            password: Optional password (mandatory if ``username`` is defined).

            client_id: Optional client identifier.

            secret: Optional client secret (mandatory if ``client_id``
                is defined).

            url: Optional platform URL (default ``https://app.alteia.com``).

            domain: Optional domain.

            proxy_url: Optional proxy URL.

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

        defaults = {
            'url': 'https://app.alteia.com',
            'connection': {'disable_ssl_certificate': True}
        }

        connection_params = kwargs
        for param_name, value in (('user', user),
                                  ('password', password),
                                  ('client_id', client_id),
                                  ('secret', secret),
                                  ('url', url),
                                  ('domain', domain),
                                  ('proxy_url', proxy_url)):
            if value is not None:
                connection_params[param_name] = value

        super().__init__(defaults=defaults, custom=custom_conf, **connection_params)
