import json

from alteia.core.resources.projectmngt.projects import Project
from alteia.core.resources.resource import Resource
from tests.core.resource_test_base import ResourcesTestBase
from tests.url_mock import Responses

responses = Responses()

MISSION_CREATION_RESP_BODY = """
    {
    "name": "mission_name",
    "project": "project_id",
    "survey_date": "2019-06-01T00:00:00.000Z"
    }
    """

SURVEY_CREATION_RESP_BODY = """
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
        responses.add(
            "POST",
            "/project-manager/missions",
            body=self.__create_mission_post_response(),
            status=200,
            content_type="application/json",
        )

        project = Project(id="project_id")
        self.sdk.missions.create_mission(
            project=project.id,
            survey_date="2019-06-01T00:00:00.000Z",
            name="mission_name",
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/missions")
        self.assertEqual(json.loads(calls[0].request.body), json.loads(MISSION_CREATION_RESP_BODY))

    @responses.activate
    def test_create_survey(self):
        responses.add(
            "POST",
            "/project-manager/projects/survey",
            body=self.__create_survey_post_response(),
            status=200,
            content_type="application/json",
        )

        self.maxDiff = None
        self.sdk.missions.create_survey(
            name="survey_name",
            project="project_id",
            survey_date="2019-06-01T00:00:00.000Z",
            number_of_images=10,
            coordinates=[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
            area=100,
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/projects/survey")
        self.assertEqual(json.loads(calls[0].request.body), json.loads(SURVEY_CREATION_RESP_BODY))

    @responses.activate
    def test_create_mission_without_name(self):
        responses.add(
            "POST",
            "/project-manager/missions",
            body=self.__create_mission_post_response(),
            status=200,
            content_type="application/json",
        )

        project = Project(id="project_id")
        self.sdk.missions.create_mission(project=project.id, survey_date="2019-06-01T00:00:00.000Z")

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        req = json.loads(MISSION_CREATION_RESP_BODY)
        req.pop("name")

        self.assertEqual(calls[0].request.url, "/project-manager/missions")
        self.assertEqual(json.loads(calls[0].request.body), req)

    @responses.activate
    def test_create_survey_without_name(self):
        responses.add(
            "POST",
            "/project-manager/projects/survey",
            body=self.__create_survey_post_response(),
            status=200,
            content_type="application/json",
        )

        self.maxDiff = None
        self.sdk.missions.create_survey(
            project="project_id",
            survey_date="2019-06-01T00:00:00.000Z",
            number_of_images=10,
            coordinates=[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
            area=100,
        )

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        req = json.loads(SURVEY_CREATION_RESP_BODY)
        req.pop("mission_name")
        req["name"] = ""

        self.assertEqual(calls[0].request.url, "/project-manager/projects/survey")
        self.assertEqual(json.loads(calls[0].request.body), req)

    @responses.activate
    def test_search_without_error(self):
        responses.add(
            "POST",
            "/project-manager/search-missions",
            body=self.__search_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls

        self.sdk.missions.search(filter={"_id": {"$in": ["mission-id"]}}, sort={"_id": -1})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/project-manager/search-missions")
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"_id": {"$in": ["mission-id"]}}, "limit": 100, "sort": {"_id": -1}}',
        )

        self.sdk.missions.search(filter={"project": {"$eq": "project-id"}}, limit=50)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, "/project-manager/search-missions")
        self.assertEqual(
            calls[1].request.body,
            '{"filter": {"project": {"$eq": "project-id"}}, "limit": 50}',
        )

    @responses.activate
    def test_delete(self):
        responses.add(
            "POST",
            "/project-manager/missions/delete-survey",
            body="{}",
            status=200,
            content_type="application/json",
        )

        self.sdk.missions.delete(mission="mission_id")

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/missions/delete-survey")
        self.assertEqual(calls[0].request.body, '{"mission": "mission_id"}')

    @staticmethod
    def __create_mission_post_response():
        return json.dumps({"mission": {"_id": "mission-id"}})

    @staticmethod
    def __create_survey_post_response():
        return json.dumps({"mission": {"_id": "mission-id"}, "flight": {"_id": "flight-id"}})

    @staticmethod
    def __search_post_response():
        return json.dumps(
            {
                "results": [{"_id": "mission-id", "project": "project-id"}],
                "total": 1,
            }
        )

    @staticmethod
    def __flight_Resource():
        return json.dumps({"_id": "flight-id"})

    @staticmethod
    def __describe():
        return json.dumps({"_id": "mission-id"})

    @staticmethod
    def __describes():
        return json.dumps([{"_id": "mission-id-1"}, {"_id": "mission-id-2"}])

    @responses.activate
    def test_describe(self):
        responses.add(
            "POST",
            "/project-manager/describe-mission",
            body=self.__describe(),
            status=200,
            content_type="application/json",
        )
        responses.add(
            "POST",
            "/project-manager/describe-missions",
            body=self.__describes(),
            status=200,
            content_type="application/json",
        )

        calls = responses.calls

        result_one = self.sdk.missions.describe("mission-id")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/project-manager/describe-mission")
        self.assertEqual(calls[0].request.body, '{"mission": "mission-id"}')
        self.assertTrue(isinstance(result_one, Resource))
        assert result_one.id == "mission-id"

        result_many = self.sdk.missions.describe(["mission-id-1", "mission-id-2"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, "/project-manager/describe-missions")
        self.assertEqual(calls[1].request.body, '{"missions": ["mission-id-1", "mission-id-2"]}')
        self.assertTrue(isinstance(result_many, list))
        self.assertTrue(isinstance(result_many[0], Resource))
        assert result_many[0].id == "mission-id-1"
        assert result_many[1].id == "mission-id-2"

    @responses.activate
    def test_update_name(self):
        responses.add(
            "POST",
            "/project-manager/update-mission-name",
            body=self.__update_name_post_response(),
            status=200,
            content_type="application/json",
        )

        mission = self.sdk.missions.update_name("mission-id", name="new-name")
        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/update-mission-name")
        self.assertEqual(calls[0].request.body, '{"mission": "mission-id", "name": "new-name"}')

        assert mission.id == "mission-id"
        assert mission.name == "new-name"

    @staticmethod
    def __update_name_post_response():
        return json.dumps({"_id": "mission-id", "name": "new-name"})
