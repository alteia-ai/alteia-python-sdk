import json

from urllib3_mock import Responses

from alteia.core.resources.resource import Resource
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
        responses.add('POST', '/project-manager/search-flights',
                      body=self.__search_post_response(), status=200,
                      content_type='application/json')
        calls = responses.calls

        self.sdk.flights.search(filter={'project': {'$eq': 'project-id'}}, sort={'_id': -1})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/project-manager/search-flights')
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"project": {"$eq": "project-id"}}, "limit": 100, "sort": {"_id": -1}}'
        )

        self.sdk.flights.search(filter={'mission': {'$eq': 'mission-id'}}, limit=50)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/project-manager/search-flights')
        self.assertEqual(calls[1].request.body,
                         '{"filter": {"mission": {"$eq": "mission-id"}}, "limit": 50}')

    @staticmethod
    def __search_post_response():
        return json.dumps({
            'results': [{'_id': 'flight-id', 'project': 'project-id', 'mission': 'mission-id'}],
            'total': 1,
        })

    @staticmethod
    def __describe():
        return json.dumps({"_id": "flight-id"})

    @staticmethod
    def __describes():
        return json.dumps([{"_id": "flight-id-1"}, {"_id": "flight-id-2"}])

    @responses.activate
    def test_describe(self):
        responses.add('POST', '/project-manager/describe-flight',
                      body=self.__describe(), status=200,
                      content_type='application/json')
        responses.add('POST', '/project-manager/describe-flights',
                      body=self.__describes(), status=200,
                      content_type='application/json')

        calls = responses.calls

        result_one = self.sdk.flights.describe('flight-id')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/project-manager/describe-flight')
        self.assertEqual(calls[0].request.body, '{"flight": "flight-id"}')
        self.assertTrue(isinstance(result_one, Resource))
        assert result_one.id == 'flight-id'

        result_many = self.sdk.flights.describe(['flight-id-1', 'flight-id-2'])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/project-manager/describe-flights')
        self.assertEqual(calls[1].request.body, '{"flights": ["flight-id-1", "flight-id-2"]}')
        self.assertTrue(isinstance(result_many, list))
        self.assertTrue(isinstance(result_many[0], Resource))
        assert result_many[0].id == 'flight-id-1'
        assert result_many[1].id == 'flight-id-2'

    @responses.activate
    def test_update_name(self):
        responses.add('POST', '/project-manager/update-flight-name',
                      body=self.__update_name_post_response(),
                      status=200, content_type='application/json')

        flight = self.sdk.flights.update_name('flight-id', name='new-name')
        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/project-manager/update-flight-name')
        self.assertEqual(calls[0].request.body, '{"flight": "flight-id", "name": "new-name"}')

        assert flight.id == 'flight-id'
        assert flight.name == 'new-name'

    @staticmethod
    def __update_name_post_response():
        return json.dumps({'_id': 'flight-id', 'name': 'new-name'})

    @responses.activate
    def test_update_status(self):
        responses.add('POST', '/project-manager/update-flight-status',
                      body=self.__update_status_post_response(),
                      status=200, content_type='application/json')

        flight = self.sdk.flights.update_status('flight-id', status='completed')
        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/project-manager/update-flight-status')
        self.assertEqual(calls[0].request.body, '{"flight": "flight-id", "status": "completed"}')

        assert flight.id == 'flight-id'
        assert flight.status == 'completed'

    @staticmethod
    def __update_status_post_response():
        return json.dumps({'_id': 'flight-id', 'status': 'completed'})
