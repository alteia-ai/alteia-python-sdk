import os
from unittest.mock import patch

import alteia
from tests.alteiatest import AlteiaTestBase


class ResourcesTestBase(AlteiaTestBase):

    @classmethod
    def setUpClass(cls):
        with patch('alteia.core.connection.token.TokenManager.renew_token') as mock:
            mock.return_value = None
            cls.sdk = alteia.SDK(config_path=cls.get_absolute_path("./config-test.json"))

    @staticmethod
    def get_absolute_path(file_path):
        return os.path.join(os.path.dirname(__file__), file_path)
