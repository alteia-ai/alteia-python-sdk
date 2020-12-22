import json

from urllib3_mock import Responses

from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()


class TestFlights(ResourcesTestBase):

    @staticmethod
    def __create_post_response():
        return json.dumps({
            '_id': 'flight-id'
            })

    @staticmethod
    def __create_upload_status_response():
        return 'OK'

    @responses.activate
    def test_search_without_error(self):
        responses.add('POST', '/dxpm/flights/search',
                      body=self.__search_post_response(), status=200,
                      content_type='application/json')
        calls = responses.calls

        self.sdk.flights.search(project='project-id')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/dxpm/flights/search')
        self.assertEqual(calls[0].request.body, '{"project_id": "project-id"}')

        self.sdk.flights.search(mission='mission-id')
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/dxpm/flights/search')
        self.assertEqual(calls[1].request.body, '{"mission_id": "mission-id"}')

    @staticmethod
    def __search_post_response():
        return json.dumps({
            'flights': [{'_id': 'flight-id'}]
            })
