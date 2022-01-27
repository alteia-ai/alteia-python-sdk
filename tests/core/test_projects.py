import json

from urllib3_mock import Responses

from alteia.core.errors import QueryError, ResponseError
from alteia.core.resources.resource import Resource
from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()


class TestProjects(ResourcesTestBase):

    @staticmethod
    def __legacy_describe():
        return json.dumps({'project': {"_id": "project-id"}})

    @responses.activate
    def test_create(self):
        responses.add('POST', '/project-manager/projects',
                      body=self.__legacy_describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.create(name='My project', company='COMPANY_ID')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/project-manager/projects')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'addProjectToUsers': True,
                              'name': 'My project',
                              'company': 'COMPANY_ID'})

    @responses.activate
    def test_create_with_extra_args(self):
        responses.add('POST', '/project-manager/projects',
                      body=self.__legacy_describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.create(name='My project', company='COMPANY_ID', arg2=10)

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/project-manager/projects')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'addProjectToUsers': True,
                              'name': 'My project',
                              'company': 'COMPANY_ID',
                              'arg2': 10})

    @responses.activate
    def test_search_without_error(self):
        responses.add('POST', '/project-manager/search-projects',
                      body=self.__search_post_response(), status=200,
                      content_type='application/json')
        calls = responses.calls

        self.sdk.projects.search(filter={'_id': {'$in': ['project-id']}}, sort={'_id': -1})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/project-manager/search-projects')
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"_id": {"$in": ["project-id"]}}, "limit": 100, "sort": {"_id": -1}}'
        )

        self.sdk.projects.search(filter={'search': {'$match': 'Debug project'}}, limit=50)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/project-manager/search-projects')
        self.assertEqual(calls[1].request.body,
                         '{"filter": {"search": {"$match": "Debug project"}}, "limit": 50}')

        self.sdk.projects.search(filter={'deletion_date': {'$exists': True}})
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[2].request.url, '/project-manager/search-projects')
        self.assertEqual(calls[2].request.body,
                         '{"filter": {"deletion_date": {"$exists": true}}, "limit": 100}')

    @staticmethod
    def __search_post_response():
        return json.dumps({
            'results': [{'_id': 'project-id'}],
            'total': 1,
        })

    def test_search_legacy_with_error(self):
        with self.assertRaises(QueryError):
            self.sdk.projects.search(name='My Project')
        with self.assertRaises(QueryError):
            self.sdk.projects.search(deleted=True)

    @staticmethod
    def __describe():
        return json.dumps({"_id": "project-id"})

    @staticmethod
    def __describes():
        return json.dumps([{"_id": "project-id-1"}, {"_id": "project-id-2"}])

    @responses.activate
    def test_describe(self):
        responses.add('POST', '/project-manager/describe-project',
                      body=self.__describe(), status=200,
                      content_type='application/json')
        responses.add('POST', '/project-manager/describe-projects',
                      body=self.__describes(), status=200,
                      content_type='application/json')

        calls = responses.calls

        result_one = self.sdk.projects.describe('project-id')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/project-manager/describe-project')
        self.assertEqual(calls[0].request.body, '{"project": "project-id"}')
        self.assertTrue(isinstance(result_one, Resource))
        assert result_one.id == 'project-id'

        result_many = self.sdk.projects.describe(['project-id-1', 'project-id-2'])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1].request.url, '/project-manager/describe-projects')
        self.assertEqual(calls[1].request.body, '{"projects": ["project-id-1", "project-id-2"]}')
        self.assertTrue(isinstance(result_many, list))
        self.assertTrue(isinstance(result_many[0], Resource))
        assert result_many[0].id == 'project-id-1'
        assert result_many[1].id == 'project-id-2'

    @responses.activate
    def test_describe_project_not_found(self):
        responses.add('POST', '/project-manager/describe-project',
                      body='Not Found', status=404,
                      content_type='text/plain')

        with self.assertRaises(ResponseError):
            result_project = self.sdk.projects.describe('unknown-project')
            self.assertTrue(result_project is None)

        calls = responses.calls

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, '/project-manager/describe-project')
        self.assertEqual(calls[0].request.body, '{"project": "unknown-project"}')
        self.assertEqual(calls[0].response.status, 404)

    @responses.activate
    def test_update_project_status(self):
        responses.add('POST', '/project-manager/projects/update/project-id',
                      body=self.__legacy_describe(), status=200,
                      content_type='application/json')

        result_project = self.sdk.projects.update_status(
            project='project-id', status='available')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/project-manager/projects/update/project-id')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(
            json.loads(calls[0].request.body),
            {'project': 'project-id', 'status': 'available'})
        self.assertTrue(isinstance(result_project, Resource))

    @responses.activate
    def test_delete_project(self):
        responses.add('DELETE', '/project-manager/projects/project-id',
                      body=self.__legacy_describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.delete(project='project-id')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/project-manager/projects/project-id')
        self.assertEqual(calls[0].request.method, 'DELETE')

    @responses.activate
    def test_update_name(self):
        responses.add('POST', '/project-manager/update-project-name',
                      body=self.__update_name_post_response(),
                      status=200, content_type='application/json')

        project = self.sdk.projects.update_name('project-id', name='new-name')
        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/project-manager/update-project-name')
        self.assertEqual(calls[0].request.body, '{"project": "project-id", "name": "new-name"}')

        assert project.id == 'project-id'
        assert project.name == 'new-name'

    @staticmethod
    def __update_name_post_response():
        return json.dumps({'_id': 'project-id', 'name': 'new-name'})
