import json

from urllib3_mock import Responses

from alteia.core.errors import QueryError
from alteia.core.resources.projectmngt.projects import Project
from alteia.core.resources.resource import Resource
from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()

MISSION_CREATION_RESP_BODY = \
    """
    {
    "name": "mission_name",
    "project": "project_id",
    "survey_date": "2019-06-01T00:00:00.000Z"
    }
    """

SURVEY_CREATION_RESP_BODY = \
    """
    {
    "project_id": "project_id",
    "name": "survey_name",
    "mission_name": "survey_name",
    "survey_date": "2019-06-01T00:00:00.000Z",
    "number_of_photos": 10,
    "orderAnalytic": {},
    "processSettings": {},
    "addProjectToUsers": true,
    "area": 100,
    "geometry": {
            "type": "GeometryCollection",
            "geometries": [
                {"type": "Polygon",
                    "coordinates": [[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]]
                }
            ]
        }
    }
    """


class TestMissions(ResourcesTestBase):

    @responses.activate
    def test_create_mission(self):
        responses.add('POST', '/uisrv/missions',
                      body=self.__create_mission_post_response(), status=200,
                      content_type='application/json')

        project = Project(id='project_id')
        self.sdk.missions.create_mission(
          project=project.id,
          survey_date='2019-06-01T00:00:00.000Z',
          name='mission_name'
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/missions')
        self.assertEqual(json.loads(calls[0].request.body),
                         json.loads(MISSION_CREATION_RESP_BODY))

    @responses.activate
    def test_create_survey(self):
        responses.add('POST', '/uisrv/projects/survey',
                      body=self.__create_survey_post_response(), status=200,
                      content_type='application/json')

        self.maxDiff = None
        self.sdk.missions.create_survey(
          name='survey_name',
          project='project_id',
          survey_date='2019-06-01T00:00:00.000Z',
          number_of_images=10,
          coordinates=[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
          area=100,
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/projects/survey')
        self.assertEqual(json.loads(calls[0].request.body),
                         json.loads(SURVEY_CREATION_RESP_BODY))

    @responses.activate
    def test_create_mission_without_name(self):
        responses.add('POST', '/uisrv/missions',
                      body=self.__create_mission_post_response(), status=200,
                      content_type='application/json')

        project = Project(id='project_id')
        self.sdk.missions.create_mission(
          project=project.id,
          survey_date='2019-06-01T00:00:00.000Z'
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        req = json.loads(MISSION_CREATION_RESP_BODY)
        req.pop('name')

        self.assertEqual(calls[0].request.url, '/uisrv/missions')
        self.assertEqual(json.loads(calls[0].request.body), req)

    @responses.activate
    def test_create_survey_without_name(self):
        responses.add('POST', '/uisrv/projects/survey',
                      body=self.__create_survey_post_response(), status=200,
                      content_type='application/json')

        self.maxDiff = None
        self.sdk.missions.create_survey(
          project='project_id',
          survey_date='2019-06-01T00:00:00.000Z',
          number_of_images=10,
          coordinates=[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
          area=100,
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        req = json.loads(SURVEY_CREATION_RESP_BODY)
        req.pop('mission_name')
        req['name'] = ''

        self.assertEqual(calls[0].request.url, '/uisrv/projects/survey')
        self.assertEqual(json.loads(calls[0].request.body),
                         req)

    @responses.activate
    def test_search_without_error(self):
        responses.add('POST', '/uisrv/missions/search',
                      body=self.__search_post_response(), status=200,
                      content_type='application/json')
        calls = responses.calls

        self.sdk.missions.search(missions=['mission-id'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/uisrv/missions/search')
        self.assertDictEqual(
            json.loads(calls[0].request.body),
            {"_id": ["mission-id"], "deleted": False})

        self.sdk.missions.search(project='pid')
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/uisrv/missions/search')
        self.assertDictEqual(
            json.loads(calls[1].request.body),
            {"project": "pid", "deleted": False})

    @responses.activate
    def test_search_with_error(self):
        # Test with an empty response body > raises a QueryError
        responses.add('POST', '/uisrv/missions/search',
                      body='{}', status=200,
                      content_type='application/json')

        with self.assertRaises(QueryError):
            self.sdk.missions.search(missions=['mission-id'])

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/missions/search')
        self.assertDictEqual(
            json.loads(calls[0].request.body),
            {"_id": ["mission-id"], "deleted": False})

    @responses.activate
    def test_delete(self):
        responses.add('POST', '/uisrv/missions/delete-survey',
                      body='{}', status=200,
                      content_type='application/json')

        self.sdk.missions.delete(mission='mission_id')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/missions/delete-survey')
        self.assertEqual(calls[0].request.body, '{"mission": "mission_id"}')

    @staticmethod
    def __create_mission_post_response():
        return json.dumps({'mission': {'_id': 'mission-id'}})

    @staticmethod
    def __create_survey_post_response():
        return json.dumps({
            'mission': {'_id': 'mission-id'},
            'flight': {'_id': 'flight-id'}
            })

    @staticmethod
    def __search_post_response():
        return json.dumps({
            'missions': [{'_id': 'mission-id'}]
            })

    @staticmethod
    def __flight_Resource():
        return json.dumps({
            '_id': 'flight-id'
            })

    @responses.activate
    def test_complete_survey_upload(self):
        responses.add('POST', '/dxpm/flights/flight-id/uploads/status',
                      body='OK', status=200,
                      content_type='application/json')

        obj = json.loads(self.__flight_Resource())

        flight = Resource(**obj)

        self.sdk.missions.complete_survey_upload(flight=flight.id)

        self.sdk.missions.complete_survey_upload(
            flight=flight.id, status='failed')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 2)

        self.assertEqual(
            calls[0].request.url, '/dxpm/flights/flight-id/uploads/status')
        self.assertDictEqual(
            json.loads(calls[0].request.body),
            {'_id': 'flight-id', 'status': 'complete'})

        self.assertEqual(
            calls[1].request.url, '/dxpm/flights/flight-id/uploads/status')
        self.assertDictEqual(
            json.loads(calls[1].request.body),
            {'_id': 'flight-id', 'status': 'failed'})
