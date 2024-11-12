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
                            "registry": "https://harbor.mydomain.com",
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
                "name": "Docker registry",
                "company": "507f191e810c19729de860ea",
                "credentials": {
                    "login": "login_test",
                },
                "labels": {
                    "type": "docker",
                    "registry": "https://harbor.mydomain.com",
                },
                "creation_date": "2022-09-23T12:27:36.719Z",
            }
        )

    @staticmethod
    def __legacy_create_object_storage():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "name": "aws s3",
                "company": "507f191e810c19729de860ea",
                "credentials": {
                    "type": "s3",
                },
                "labels": {
                    "type": "object-storage",
                    "bucket": "bucket.s3.us-east-1.amazonaws.com",
                },
                "creation_date": "2022-09-23T12:27:36.719Z",
            }
        )

    @staticmethod
    def __legacy_create_stac_catalog():
        return json.dumps(
            {
                "_id": "632da638c1414e6fced3aef2",
                "name": "up-42",
                "company": "507f191e810c19729de860ea",
                "credentials": {
                    "type": "oauth",
                    "token_url": "https://api.up42.com/oauth/token",
                    "client_id": "client_id",
                },
                "type": {
                    "type": "stac_catalog",
                    "catalog": "https://api.up42.com/v2/assets/stac",
                },
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
            company="507f191e810c19729de860eb",
            credentials={
                "type": "docker",
                "login": "login_test",
                "password": "password_test",
            },
            labels={
                "type": "docker",
                "registry": "https://harbor.mydomain.com",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "Docker registry", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"type": "docker", "login": "login_test", "password": "password_test"},'
            ' "labels": {"type": "docker", "registry": "https://harbor.mydomain.com"}}',
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
            company="507f191e810c19729de860eb",
            credentials={
                "type": "s3",
                "aws_access_key_id": "key_id",
                "aws_secret_access_key": "password_test",
                "aws_region": "us-east-1",
            },
            labels={
                "type": "object-storage",
                "bucket": "bucket.s3.us-east-1.amazonaws.com",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"name": "aws s3", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"type": "s3", "aws_access_key_id": "key_id", "aws_secret_access_key": "password_test",'
            ' "aws_region": "us-east-1"}, "labels": {"type": "object-storage",'
            ' "bucket": "bucket.s3.us-east-1.amazonaws.com"}}',
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
            company="507f191e810c19729de860eb",
            credentials={
                "type": "oauth",
                "token_url": "https://api.up42.com/oauth/token",
                "client_id": "client_id",
                "client_secret": "credbegin.credend",
            },
            labels={
                "type": "stac-catalog",
                "catalog": "https://api.up42.com/v2/assets/stac",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )

        self.assertEqual(
            calls[0].request.body,
            '{"name": "up-42", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"type": "oauth", "token_url": "https://api.up42.com/oauth/token",'
            ' "client_id": "client_id",'
            ' "client_secret": "credbegin.credend"},'
            ' "labels": {"type": "stac-catalog", "catalog": "https://api.up42.com/v2/assets/stac"}}',
        )

    @responses.activate
    def test_credentials_create_without_label(self):
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
            company="507f191e810c19729de860eb",
            credentials={
                "login": "login_test",
                "password": "password_test",
            }
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "Docker registry", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"login": "login_test", "password": "password_test"}}',
        )

    @responses.activate
    def test_credentials_create_without_type(self):
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
            company="507f191e810c19729de860eb",
            credentials={
                "login": "login_test",
                "password": "password_test",
            },
            labels={
                "registry": "https://harbor.mydomain.com",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "Docker registry", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"login": "login_test", "password": "password_test"},'
            ' "labels": {"registry": "https://harbor.mydomain.com"}}',
        )

    @responses.activate
    def test_credentials_create_docker_without_type(self):
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
            company="507f191e810c19729de860eb",
            credentials={
                "login": "login_test",
                "password": "password_test",
            },
            labels={
                "registry": "https://harbor.mydomain.com"
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "Docker registry", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"login": "login_test", "password": "password_test"},'
            ' "labels": {"registry": "https://harbor.mydomain.com"}}',
        )

    @responses.activate
    def test_credentials_create_s3_without_type(self):
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
            company="507f191e810c19729de860eb",
            credentials={
                "aws_access_key_id": "key_id",
                "aws_secret_access_key": "password_test",
                "aws_region": "us-east-1",
            },
            labels={
                "bucket": "bucket.s3.us-east-1.amazonaws.com",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "aws s3", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"aws_access_key_id": "key_id", "aws_secret_access_key": "password_test",'
            ' "aws_region": "us-east-1"}, "labels": {"bucket": "bucket.s3.us-east-1.amazonaws.com"}}',
        )

    @responses.activate
    def test_credentials_create_stac_catalog_without_type(self):
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
            company="507f191e810c19729de860eb",
            credentials={
                "token_url": "https://api.up42.com/oauth/token",
                "client_id": "client_id",
                "client_secret": "credbegin.credend",
            },
            labels={
                "catalog": "https://api.up42.com/v2/assets/stac",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/create-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"name": "up-42", "company": "507f191e810c19729de860eb",'
            ' "credentials": {"token_url": "https://api.up42.com/oauth/token",'
            ' "client_id": "client_id",'
            ' "client_secret": "credbegin.credend"},'
            ' "labels": {"catalog": "https://api.up42.com/v2/assets/stac"}}',
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

    @responses.activate
    def test_set_credentials(self):
        responses.add(
            "POST",
            "/credentials-service/set-credentials",
            status=200,
            content_type="application/json",
            body=self.__legacy_create_docker()
        )
        calls = responses.calls
        self.sdk.credentials.set_credentials(
            company="507f191e810c19729de860ea",
            name="Docker registry",
            credentials={
                "type": "docker",
                "login": "login_test",
                "password": "password_test",
                "registry": "https://harbor.mydomain.com",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/set-credentials"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860ea", "name": "Docker registry",'
            ' "credentials": {"type": "docker", "login": "login_test", "password": "password_test",'
            ' "registry": "https://harbor.mydomain.com"}}',
        )

    @responses.activate
    def test_set_labels(self):
        responses.add(
            "POST",
            "/credentials-service/set-labels",
            status=200,
            content_type="application/json",
            body=self.__legacy_create_docker()
        )
        calls = responses.calls
        self.sdk.credentials.set_labels(
            company="507f191e810c19729de860ea",
            name="Docker registry",
            labels={
                "label1": "value1",
                "label2": "value2",
                "label3": "value3",
            },
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/credentials-service/set-labels"
        )
        self.assertEqual(
            calls[0].request.body,
            '{"company": "507f191e810c19729de860ea", "name": "Docker registry",'
            ' "labels": {"label1": "value1", "label2": "value2", "label3": "value3"}}',
        )
