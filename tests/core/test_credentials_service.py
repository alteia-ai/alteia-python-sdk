import json

import pytest
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
    def __legacy_create_docker():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "type": "docker",
                "name": "Docker registry",
                "credentials": {
                    "type": "docker",
                    "registry": "https://harbor.dev-tool.delair-stack.com",
                    "login": "login_test",
                },
                "company": "507f191e810c19729de860ea",
                "creation_date": "2022-09-23T12:27:36.719Z",
            }
        )

    @staticmethod
    def __legacy_create_object_storage():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "type": "object-storage",
                "name": "aws s3",
                "credentials": {
                    "type": "s3",
                    "bucket": "bucket.s3.us-east-1.amazonaws.com",
                },
                "company": "507f191e810c19729de860ea",
                "creation_date": "2022-09-23T12:27:36.719Z",
            }
        )

    @staticmethod
    def __legacy_create_stac_catalog():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "type": "stac_catalog",
                "name": "up-42",
                "credentials": {
                    "type": "oauth",
                    "token_url": "https://api.up42.com/oauth/token",
                    "client_id": "711071f4-6480-40ba-92d9-5c21f10bff9a",
                    "catalog": "https://api.up42.com/v2/assets/stac",
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
            filter={
                "company": {"$eq": "507f191e810c19729de860eb"},
                "name": {"$eq": "Docker registry production"},
            }
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/search-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"company": {"$eq": "507f191e810c19729de860eb"},'
            ' "name": {"$eq": "Docker registry production"}}}',
        )

    @responses.activate
    def test_credentials_create_docker(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_docker(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="Docker registry",
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
            '{"company": "507f191e810c19729de860eb", "name": "Docker registry",'
            ' "type": "docker", "credentials": {"type": "docker", "login": "login_test",'
            ' "password": "password_test", "registry": "https://harbor.dev-tool.delair-stack.com"}}',
        )

    @responses.activate
    def test_credentials_create_object_storage(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_object_storage(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="aws s3",
            credentials_type="object-storage",
            credentials={
                "type": "s3",
                "aws_access_key_id": "key_id",
                "aws_secret_access_key": "password_test",
                "aws_region": "us-east-1",
                "bucket": "bucket.s3.us-east-1.amazonaws.com",
            },
            company="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "name": "aws s3", "type": "object-storage",'
            ' "credentials": {"type": "s3", "aws_access_key_id": "key_id", "aws_secret_access_key": "password_test",'
            ' "aws_region": "us-east-1", "bucket": "bucket.s3.us-east-1.amazonaws.com"}}',
        )

    @responses.activate
    def test_credentials_create_stac_catalog(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_stac_catalog(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="up-42",
            credentials_type="stac-catalog",
            credentials={
                "type": "oauth",
                "token_url": "https://api.up42.com/oauth/token",
                "client_id": "711071f4-6480-40ba-92d9-5c21f10bff9a",
                "client_secret": "pNHY91qi.NAEIsRdYwFWt0aZxDXyd0Wp3fzrOO0EnEem",
                "catalog": "https://api.up42.com/v2/assets/stac",
            },
            company="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "name": "up-42", "type": "stac-catalog",'
            ' "credentials": {"type": "oauth", "token_url": "https://api.up42.com/oauth/token",'
            ' "client_id": "711071f4-6480-40ba-92d9-5c21f10bff9a",'
            ' "client_secret": "pNHY91qi.NAEIsRdYwFWt0aZxDXyd0Wp3fzrOO0EnEem",'
            ' "catalog": "https://api.up42.com/v2/assets/stac"}}',
        )

    @responses.activate
    def test_credentials_create_type_None(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_docker(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="Docker registry",
            credentials_type=None,
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
            '{"company": "507f191e810c19729de860eb", "name": "Docker registry", "type": "docker",'
            ' "credentials": {"type": "docker", "login": "login_test", "password": "password_test",'
            ' "registry": "https://harbor.dev-tool.delair-stack.com"}}',
        )

    @responses.activate
    def test_credentials_no_create_bad_type(self):
        with pytest.raises(Exception) as excinfo:
            self.sdk.credentials.create(
                name="Docker registry",
                credentials_type="bad_type",
                credentials={
                    "type": "docker",
                    "login": "login_test",
                    "password": "password_test",
                    "registry": "https://harbor.dev-tool.delair-stack.com",
                },
                company="507f191e810c19729de860eb",
            )

        self.assertEqual(str(excinfo.value), "Type of credentials is wrong")

    @responses.activate
    def test_credentials_no_create_unknwon_type(self):
        with pytest.raises(Exception) as excinfo:
            self.sdk.credentials.create(
                name="test",
                credentials_type=None,
                credentials={
                    "type": "unknwon_type",
                    "login": "login_test",
                    "password": "password_test",
                    "registry": "https://harbor.dev-tool.delair-stack.com",
                },
                company="507f191e810c19729de860eb",
            )

        self.assertEqual(
            str(excinfo.value),
            "Impossible to retrieve credentials type from unknwon_type",
        )

    @responses.activate
    def test_credentials_create_docker_without_credentials_type(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_docker(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="Docker registry",
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
            '{"company": "507f191e810c19729de860eb", "name": "Docker registry", "type": "docker",'
            ' "credentials": {"type": "docker", "login": "login_test", "password": "password_test",'
            ' "registry": "https://harbor.dev-tool.delair-stack.com"}}',
        )

    @responses.activate
    def test_credentials_create_s3_without_credentials_type(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_object_storage(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="aws s3",
            credentials={
                "type": "s3",
                "aws_access_key_id": "key_id",
                "aws_secret_access_key": "password_test",
                "aws_region": "us-east-1",
                "bucket": "bucket.s3.us-east-1.amazonaws.com",
            },
            company="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "name": "aws s3", "type": "object-storage",'
            ' "credentials": {"type": "s3", "aws_access_key_id": "key_id", "aws_secret_access_key": "password_test",'
            ' "aws_region": "us-east-1", "bucket": "bucket.s3.us-east-1.amazonaws.com"}}',
        )

    @responses.activate
    def test_credentials_create_stac_catalog_without_credentials_type(self):
        responses.add(
            "POST",
            "/credentials-service/create-credentials",
            body=self.__legacy_create_stac_catalog(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.credentials.create(
            name="up-42",
            credentials={
                "type": "oauth",
                "token_url": "https://api.up42.com/oauth/token",
                "client_id": "711071f4-6480-40ba-92d9-5c21f10bff9a",
                "client_secret": "pNHY91qi.NAEIsRdYwFWt0aZxDXyd0Wp3fzrOO0EnEem",
                "catalog": "https://api.up42.com/v2/assets/stac",
            },
            company="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860eb", "name": "up-42", "type": "stac-catalog",'
            ' "credentials": {"type": "oauth", "token_url": "https://api.up42.com/oauth/token",'
            ' "client_id": "711071f4-6480-40ba-92d9-5c21f10bff9a",'
            ' "client_secret": "pNHY91qi.NAEIsRdYwFWt0aZxDXyd0Wp3fzrOO0EnEem",'
            ' "catalog": "https://api.up42.com/v2/assets/stac"}}',
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
