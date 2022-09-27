import json

from urllib3_mock import Responses

from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()


PILOT_RESPONSE = {
    "_id": "61968597ef6070b5ad4ea16f",
    "creation_date": "2021-11-18T16:55:51.362Z",
    "modification_date": "2021-11-18T16:55:51.362Z",
    "creation_user": "5fca030d5014570006d30b3d",
    "modification_user": "5fca030d5014570006d30b3d",
    "user": "60bf8cc7b5d4fb00060e6c22",
    "teams": ["6039093f60ecb706590775da"],
    "sensor_models": [],
    "carrier_models": [],
    "companies": ["5f900f82bc50ff000650abe7"],
}


class TestPilots(ResourcesTestBase):
    @responses.activate
    def test_single_pilot_describe(self):
        responses.add(
            "POST",
            "/dct-service/asset-management/describe-pilot",
            body=self.__describe_single_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.pilots.describe("pilot-id-1")

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/dct-service/asset-management/describe-pilot"
        )
        self.assertEqual(calls[0].request.body, '{"pilot": "pilot-id-1"}')

    @responses.activate
    def test_multiple_pilot_describe(self):
        responses.add(
            "POST",
            "/dct-service/asset-management/describe-pilots",
            body=self.__describe_multi_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.pilots.describe(["pilot-id-1", "pilot-id-2"])

        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].request.url, "/dct-service/asset-management/describe-pilots"
        )
        self.assertEqual(
            calls[0].request.body, '{"pilots": ["pilot-id-1", "pilot-id-2"]}'
        )

    @staticmethod
    def __describe_single_post_response():
        return json.dumps(PILOT_RESPONSE)

    @staticmethod
    def __describe_multi_post_response():
        return json.dumps([PILOT_RESPONSE] * 2)
