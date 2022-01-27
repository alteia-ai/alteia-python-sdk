import json
from unittest import mock

import alteia
from alteia.core.connection.abstract_connection import DEFAULT_USER_AGENTS
from tests.core.resource_test_base import ResourcesTestBase

BASE_USER_AGENT = ' '.join(reversed(DEFAULT_USER_AGENTS))
DEFAULT_MOCK_CONTENT = {'url': 'some url',
                        'connection': {
                            'max_retries': 1,
                            'disable_ssl_certificate': True}}


class TestSDK(ResourcesTestBase):
    def test_resource_attributes(self):
        self.assertIsInstance(self.sdk.missions,
                              alteia.apis.client.projectmngt.missionsimpl.MissionsImpl)

        attrs = dir(self.sdk)
        self.assertIn('annotations',  attrs)
        self.assertIn('flights', attrs)
        self.assertIn('missions', attrs)
        self.assertIn('projects', attrs)
        self.assertIn('datasets', attrs)

    @mock.patch('alteia.core.config.read_file')
    def test_missing_url(self, mock_read_file):
        mock_read_file.return_value = json.dumps({})
        with self.assertRaises(alteia.core.errors.ConfigError):
            alteia.SDK()

    @mock.patch('alteia.core.config.read_file')
    def test_missing_credentials(self, mock_read_file):
        mock_read_file.return_value = json.dumps({'url': 'some url'})
        with self.assertRaises(alteia.core.errors.ConfigError):
            alteia.SDK()

    @mock.patch('alteia.core.config.read_file')
    def test_wrong_config(self, mock_read_file):
        mock_read_file.return_value = '{"content":"content"}'
        with self.assertRaises(Exception):
            alteia.SDK(user='username', password='password')

    @mock.patch('alteia.core.connection.token.TokenManager.renew_token')
    def test_renew_token_at_init(self, mock):
        alteia.SDK(user='username', password='password')
        self.assertTrue(mock.called)

    @mock.patch('alteia.core.connection.token.TokenManager.renew_token')
    def test_user_agent(self, *args):
        sdk = alteia.SDK(user='username', password='password')
        self.assertEqual(sdk._connection.user_agent,
                         f'{sdk._name} {BASE_USER_AGENT}')

        sdk = alteia.SDK(user='username', password='password', service='service-foobar')
        self.assertEqual(sdk._connection.user_agent,
                         f'service-foobar {sdk._name} {BASE_USER_AGENT}')
