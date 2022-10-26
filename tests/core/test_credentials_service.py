import json

from urllib3_mock import Responses

from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()


class TestCredentials(ResourcesTestBase):
    @staticmethod
    def __legacy_search():
        return json.dumps(
            {
                "total": 1,
                "results": [
                    {
                        "_id": "632da638c1414e6fced3aef2",
                        "type": "docker",
                        "name": "Docker registry production",
                        "credentials": {
                            "type": "docker",
                            "registry": "https://harbor.dev-tool.delair-stack.com",
                            "login": "login_test",
                        },
                        "company": "507f191e810c19729de860ea",
                        "creation_date": "2022-09-23T12:27:36.719Z",
                    }
                ],
            }
        )

    @staticmethod
    def __legacy_create():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "type": "docker",
                "name": "Docker registry production",
                "credentials": {
                    "type": "docker",
                    "registry": "https://harbor.dev-tool.delair-stack.com",
                    "login": "login_test",
                },
                "company": "507f191e810c19729de860ea",
                "creation_date": "2022-09-23T12:27:36.719Z",
            }
        )

    @responses.activate
    def test_credentials_search(self):
        responses.add(
            "POST",
            "/credentials-service/search-credentials",
            body=self.__legacy_search(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.search(
            filter={"company": {"$eq": "507f191e810c19729de860eb"}, "name": {"$eq": "Docker registry production"}}
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/search-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"company": {"$eq": "507f191e810c19729de860eb"}, "name": {"$eq": "Docker registry production"}}}',
        )

    @responses.activate
    def test_credentials_create(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="test",
            credentials_type="docker",
            credentials={
                "type": "docker",
                "login": "login_test",
                "password": "password_test",
                "registry": "https://harbor.dev-tool.delair-stack.com",
            },
            company="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "name": "test", "type": "docker", "credentials": {"type": "docker", "login": "login_test", "password": "password_test", "registry": "https://harbor.dev-tool.delair-stack.com"}}'
         )

    @responses.activate
    def test_credentials_delete(self):
        responses.add(
            "POST",
            "/credentials-service/delete-credentials",
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.delete(
            credential="63317316dfaf18df1b77f42f", company="507f191e810c19729de860eb"
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/delete-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "credentials": "63317316dfaf18df1b77f42f"}',
        )
