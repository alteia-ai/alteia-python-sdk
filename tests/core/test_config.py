import json
import os.path
from unittest import mock

from alteia.core.config import ConnectionConfig
from tests.alteiatest import AlteiaTestBase

DEFAULT_MOCK_CONTENT = {
    "password": "default password",
    "user": "default user",
    "client_secret": "default secret",
    "url": "default url",
    "connection": {"max_retries": 1, "disable_ssl_certificate": True},
}


class TestConnectionConfig(AlteiaTestBase):
    """Tests for connection configuration."""

    def test_default_config(self):
        """Test default configuration."""
        conf = ConnectionConfig()
        self.assertEqual(conf.url, "https://app.alteia.com")
        self.assertEqual(conf.connection["disable_ssl_certificate"], True)

    def test_complete_custom_config(self):
        """Test loading a complete custom configuration."""
        conf_path = os.path.join(os.path.dirname(__file__), "config-complete-connection.json")
        conf = ConnectionConfig(file_path=conf_path)
        self.assertEqual(conf.user, "user")
        self.assertEqual(conf.password, "password")
        self.assertEqual(conf.client_secret, "secret")
        self.assertEqual(conf.url, "https://app.alteia.com")
        self.assertEqual(conf.connection["max_retries"], 10)
        self.assertEqual(conf.connection["disable_ssl_certificate"], False)

    def test_partial_custom_config(self):
        """Test loading a partial custom configuration."""
        conf_path = os.path.join(os.path.dirname(__file__), "config-partial-connection.json")
        conf = ConnectionConfig(file_path=conf_path)

        self.assertEqual(conf.user, "user")
        self.assertEqual(conf.connection["disable_ssl_certificate"], False)

    def test_override_default_config(self):
        """Test overloading default configuration with keywords arguments."""
        with mock.patch("alteia.core.config.read_file") as mock_read_file:
            mock_read_file.return_value = json.dumps(DEFAULT_MOCK_CONTENT)
            conf = ConnectionConfig(user="other")
            self.assertEqual(conf.user, "other")
            self.assertEqual(conf.url, "https://app.alteia.com")
            self.assertEqual(conf.connection["disable_ssl_certificate"], True)

    def test_override_custom_config(self):
        """Test overloading custom configuration with keywords arguments."""
        conf_path = os.path.join(os.path.dirname(__file__), "config-partial-connection.json")
        conf = ConnectionConfig(file_path=conf_path, user="username")
        self.assertEqual(conf.user, "username")
        self.assertEqual(conf.url, "https://app.alteia.com")
        self.assertEqual(conf.connection["disable_ssl_certificate"], False)
