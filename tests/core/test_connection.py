"""Tests related to connections."""

import json
import unittest
from unittest.mock import MagicMock, patch

import urllib3

from alteia.core.connection.abstract_connection import DEFAULT_USER_AGENTS
from alteia.core.connection.connection import AsyncConnection, Connection
from alteia.core.connection.credentials import ClientCredentials
from alteia.core.connection.token import TokenManager
from alteia.core.errors import ResponseError
from tests.alteiatest import AlteiaTestBase

BASE_USER_AGENT = " ".join(reversed(DEFAULT_USER_AGENTS))
DEFAULT_HEADERS = {
    "User-Agent": BASE_USER_AGENT,
    "referer": "https://app.alteia.com",
}


@patch.object(urllib3.PoolManager, "request")
class TestConnection(AlteiaTestBase):
    """Tests synchronous connection."""

    def setUp(self):
        creds = ClientCredentials(client_id="fake_client_id", client_secret="fake_client_secret")
        conn_opts = {"base_url": "https://app.alteia.com", "credentials": creds}
        self.conn = Connection(**conn_opts)

    def test_post(self, mocked_req):
        """Test POST with different arguments."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        resp_data = self.conn.post("/path")
        self.assertEqual(resp_data, "received data")
        mocked_req.assert_called_once()
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "body": {},
                "headers": DEFAULT_HEADERS,
                "method": "POST",
                "timeout": 600.0,
                "preload_content": True,
                "url": "https://app.alteia.com/path",
            },
        )

        mocked_req.clear()
        mocked_req.return_value.data = '{"key": "value"}'.encode("utf-8")
        resp_data = self.conn.post(
            "other",
            data="data to send",
            headers={"Custom-Header": "Test"},
            timeout=15.0,
            as_json=True,
        )
        self.assertDictEqual(resp_data, {"key": "value"})
        self.assertEqual(mocked_req.call_count, 2)
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        headers = DEFAULT_HEADERS.copy()
        headers["Custom-Header"] = "Test"
        self.assertDictEqual(
            call_args,
            {
                "body": "data to send",
                "headers": headers,
                "method": "POST",
                "preload_content": True,
                "timeout": 15.0,
                "url": "https://app.alteia.com/other",
            },
        )

    def test_post_failure(self, mocked_req):
        """Test POST with failure."""
        mocked_req.return_value = MagicMock(
            status=400, data='{"code":"raise","message":"msg","service":"my-service","foo":"bar"}'
        )

        with self.assertRaises(ResponseError) as rex:
            self.conn.post("/path")
        assert rex.exception.status == 400
        assert isinstance(rex.exception.data, dict)
        assert rex.exception.data.get("foo") == "bar"
        assert rex.exception.code == "raise"
        assert rex.exception.service == "my-service"
        assert rex.exception.message == "msg"
        assert rex.exception.details is None

        mocked_req.assert_called_once()

    def test_get(self, mocked_req):
        """Test GET."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        resp_data = self.conn.get("/path")
        self.assertEqual(resp_data, "received data")
        mocked_req.assert_called_once()
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "headers": DEFAULT_HEADERS,
                "method": "GET",
                "timeout": 600.0,
                "preload_content": True,
                "url": "https://app.alteia.com/path",
            },
        )

        mocked_req.clear()
        mocked_req.return_value.data = '{"key": "value"}'.encode("utf-8")
        resp_data = self.conn.get("other", headers={"Custom-Header": "Test"}, timeout=15.0, as_json=True)
        self.assertDictEqual(resp_data, {"key": "value"})
        self.assertEqual(mocked_req.call_count, 2)
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        headers = DEFAULT_HEADERS.copy()
        headers["Custom-Header"] = "Test"
        self.assertDictEqual(
            call_args,
            {
                "headers": headers,
                "method": "GET",
                "timeout": 15.0,
                "preload_content": True,
                "url": "https://app.alteia.com/other",
            },
        )

    def test_get_failure(self, mocked_req):
        """Test GET with failure."""
        mocked_req.return_value = MagicMock(status=500, data="received data")

        with self.assertRaises(ResponseError) as rex:
            self.conn.get("/path")
        assert rex.exception.status == 500
        assert rex.exception.data == "received data"
        assert rex.exception.code is None
        assert rex.exception.service is None
        assert rex.exception.message is None
        assert rex.exception.details is None

        mocked_req.assert_called_once()

    def test_get_with_expired_token(self, mocked_req):
        """Test GET with expired token."""
        token_post_resp = {
            "access_token": "y77ceIHcPu2RKHo9clekkG8B",
            "expires_in": 14400,
            "refresh_token": "0PPCsHkBesbVC2FJpV8eqaXB",
            "token_type": "Bearer",
        }
        values = [
            MagicMock(status=401, data=""),
            MagicMock(status=200, data=json.dumps(token_post_resp).encode("utf-8")),
            MagicMock(status=200, data="received data"),
        ]
        mocked_req.side_effect = values

        resp_data = self.conn.get("/path")
        self.assertEqual(resp_data, "received data")
        self.assertEqual(mocked_req.call_count, 3)

    def test_lazy_get(self, mocked_req):
        """Test lazy GET."""
        mocked_req.return_value = MagicMock(status=200, data="received data")
        self.conn.get("/path", preload_content=False)
        mocked_req.assert_called_once()
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "headers": DEFAULT_HEADERS,
                "method": "GET",
                "preload_content": False,
                "timeout": 600.0,
                "url": "https://app.alteia.com/path",
            },
        )

    def test_put(self, mocked_req):
        """Test PUT."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        resp_data = self.conn.put("/path")
        self.assertEqual(resp_data, "received data")
        mocked_req.assert_called_once()
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "body": {},
                "headers": DEFAULT_HEADERS,
                "method": "PUT",
                "timeout": 600.0,
                "preload_content": True,
                "url": "https://app.alteia.com/path",
            },
        )

        mocked_req.clear()
        mocked_req.return_value.data = '{"key": "value"}'.encode("utf-8")
        resp_data = self.conn.put(
            "other",
            data="data to send",
            headers={"Custom-Header": "Test"},
            timeout=15.0,
            as_json=True,
        )
        self.assertDictEqual(resp_data, {"key": "value"})
        self.assertEqual(mocked_req.call_count, 2)
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        headers = DEFAULT_HEADERS.copy()
        headers["Custom-Header"] = "Test"
        self.assertDictEqual(
            call_args,
            {
                "body": "data to send",
                "headers": headers,
                "method": "PUT",
                "timeout": 15.0,
                "preload_content": True,
                "url": "https://app.alteia.com/other",
            },
        )

    def test_put_failure(self, mocked_req):
        """Test PUT with failure."""
        mocked_req.return_value = MagicMock(
            status=500, data='{"code":"raise","message":"msg","service":"my-service","details":"..."}'
        )

        with self.assertRaises(ResponseError) as rex:
            self.conn.put("/path")
        assert rex.exception.status == 500
        assert isinstance(rex.exception.data, dict)
        assert rex.exception.code == "raise"
        assert rex.exception.service == "my-service"
        assert rex.exception.message == "msg"
        assert rex.exception.details == "..."

        mocked_req.assert_called_once()

    def test_delete(self, mocked_req):
        """Test delete."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        resp_data = self.conn.delete("/path")
        self.assertEqual(resp_data, "received data")
        mocked_req.assert_called_once()
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "body": {},
                "headers": DEFAULT_HEADERS,
                "method": "DELETE",
                "timeout": 600.0,
                "url": "https://app.alteia.com/path",
            },
        )

        mocked_req.clear()
        mocked_req.return_value.data = '{"key": "value"}'.encode("utf-8")
        resp_data = self.conn.delete(
            "other",
            data="data to send",
            headers={"Custom-Header": "Test"},
            timeout=15.0,
            as_json=True,
        )
        self.assertDictEqual(resp_data, {"key": "value"})
        self.assertEqual(mocked_req.call_count, 2)
        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        headers = DEFAULT_HEADERS.copy()
        headers["Custom-Header"] = "Test"
        self.assertDictEqual(
            call_args,
            {
                "body": "data to send",
                "headers": headers,
                "method": "DELETE",
                "timeout": 15.0,
                "url": "https://app.alteia.com/other",
            },
        )

    def test_delete_failure(self, mocked_req):
        """Test DELETE with failure."""
        mocked_req.return_value = MagicMock(status=500)

        with self.assertRaises(ResponseError):
            self.conn.delete("/path")

        mocked_req.assert_called_once()

    def test_user_agent(self, *args):
        """Test playing with User-Agent"""

        self.assertEqual(self.conn.user_agent, BASE_USER_AGENT)

        self.conn.set_user_agent("new-UA/1.0")
        self.assertEqual(self.conn.user_agent, f"new-UA/1.0 {BASE_USER_AGENT}")

        self.conn.set_user_agent("another/0.6")
        self.assertEqual(self.conn.user_agent, f"another/0.6 new-UA/1.0 {BASE_USER_AGENT}")

        self.conn.set_user_agent("another/2.0", remove_last=True)
        self.assertEqual(self.conn.user_agent, f"another/2.0 new-UA/1.0 {BASE_USER_AGENT}")

        self.conn.set_user_agent("foobar/1.0", reset_to_default=True)
        self.assertEqual(self.conn.user_agent, f"foobar/1.0 {BASE_USER_AGENT}")

        self.conn.set_user_agent("the-last/1.0", remove_all=True)
        self.assertEqual(self.conn.user_agent, "the-last/1.0")

        self.conn.set_user_agent("", reset_to_default=True)
        self.assertEqual(self.conn.user_agent, BASE_USER_AGENT)


@unittest.skip("Work in progress...")
@patch.object(urllib3.PoolManager, "request")
@patch("requests_futures.sessions.FuturesSession", autospec=True)
class TestAsynchronousConnection(AlteiaTestBase):
    """Tests asynchronous connection."""

    def setUp(self):
        base_url = "https://localhost"
        creds = ClientCredentials(client_id="fake_client_id", client_secret="fake_client_secret")
        token_mngr = TokenManager(connection=AsyncConnection, credentials=creds)

        conn_opts = {
            "base_url": base_url,
            "token_manager": token_mngr,
            "disable_ssl_certificate": True,
            "retries": 1,
        }

        self.conn = AsyncConnection(**conn_opts)

    def test_put(self, mocked_session, mocked_req):
        """Test PUT."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        aresp = self.conn.put("/path")
        resp = aresp.result()
        self.assertEqual(resp.content, "received data")
        mocked_req.assert_called_once()

        call_args = mocked_req.call_args[1]
        del call_args["retries"]
        self.assertDictEqual(
            call_args,
            {
                "body": {},
                "headers": DEFAULT_HEADERS,
                "method": "PUT",
                "timeout": 600.0,
                "url": "https://app.alteia.com/path",
            },
        )

    def test_put_failure(self, mocked_session, mocked_req):
        """Test PUT with failure."""
        mocked_req.return_value = MagicMock(status=200, data="received data")

        aresp = self.conn.put("/path")
        resp = aresp.result()
        self.assertEqual(resp.content, "received data")
        mocked_req.assert_called_once()
