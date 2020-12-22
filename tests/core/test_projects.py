import json

from urllib3_mock import Responses

from alteia.core.errors import QueryError
from alteia.core.resources.resource import Resource
from tests.core.resource_test_base import ResourcesTestBase

responses = Responses()


class TestProjects(ResourcesTestBase):

    @responses.activate
    def test_create(self):
        responses.add('POST', '/uisrv/projects',
                      body=self.__describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.create(name='My project')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/projects')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'addProjectToUsers': True,
                              'name': 'My project'})

    @responses.activate
    def test_create_with_extra_args(self):
        responses.add('POST', '/uisrv/projects',
                      body=self.__describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.create(name='My project', arg2=10)

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/projects')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'addProjectToUsers': True,
                              'name': 'My project', 'arg2': 10})

    @responses.activate
    def test_search(self):
        responses.add('POST', '/uisrv/projects/search',
                      body=self.__search(), status=200,
                      content_type='application/json')

        result_projects = self.sdk.projects.search(name='Debug projectm')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/projects/search')
        self.assertEqual(calls[0].request.method, 'POST')

        self.assertEqual(
            json.loads(calls[0].request.body), {"search": "Debug projectm",
                                                "deleted": False})

        self.assertEqual(len(result_projects), 1)
        self.assertTrue(isinstance(result_projects[0], Resource))

    @responses.activate
    def test_search_deleted(self):
        responses.add('POST', '/uisrv/projects/search',
                      body=self.__search(), status=200,
                      content_type='application/json')

        result_projects = self.sdk.projects.search(name='Debug projectm',
                                                   deleted=True)

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, '/uisrv/projects/search')
        self.assertEqual(calls[0].request.method, 'POST')

        self.assertEqual(
            json.loads(calls[0].request.body), {"search": "Debug projectm",
                                                "deleted": True})

        self.assertEqual(len(result_projects), 1)
        self.assertTrue(isinstance(result_projects[0], Resource))

    @responses.activate
    def test_search_with_errors(self):
        responses.add('POST', '/uisrv/projects/search',
                      body=self.__search_wrong(), status=200,
                      content_type='application/json')

        with self.assertRaises(QueryError):
            self.sdk.projects.search(name='Debug projectm')

    def __search(self):
        return json.dumps({'projects': [{
            "_id": "project-id"
            }]})

    def __search_wrong(self):
        return json.dumps([{
            "_id": "project-id"
            }])

    def __describe(self):
        return json.dumps({'project': {"_id": "project-id"}})

    @responses.activate
    def test_describe(self):
        responses.add('POST', '/uisrv/projects/project-id',
                      body=self.__describe(), status=200,
                      content_type='application/json')

        result_project = self.sdk.projects.describe(project='project-id')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/uisrv/projects/project-id')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'deleted': False})
        self.assertTrue(isinstance(result_project, Resource))

    @responses.activate
    def test_describe_project_not_found(self):
        responses.add('POST', '/uisrv/projects/unknown-project',
                      body='Not Found', status=404,
                      content_type='text/plain')

        result_project = self.sdk.projects.describe('unknown-project',
                                                    deleted=True)

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/uisrv/projects/unknown-project')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(json.loads(calls[0].request.body),
                             {'deleted': True})
        self.assertTrue(result_project is None)

    @responses.activate
    def test_update_project_status(self):
        responses.add('POST', '/uisrv/projects/update/project-id',
                      body=self.__describe(), status=200,
                      content_type='application/json')

        result_project = self.sdk.projects.update_status(
            project='project-id', status='available')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/uisrv/projects/update/project-id')
        self.assertEqual(calls[0].request.method, 'POST')
        self.assertDictEqual(
            json.loads(calls[0].request.body),
            {'project': 'project-id', 'status': 'available'})
        self.assertTrue(isinstance(result_project, Resource))

    @responses.activate
    def test_delete_project(self):
        responses.add('DELETE', '/uisrv/projects/project-id',
                      body=self.__describe(), status=200,
                      content_type='application/json')

        self.sdk.projects.delete(project='project-id')

        calls = responses.calls

        # test responses
        self.assertEqual(len(calls), 1)

        self.assertEqual(
            calls[0].request.url, '/uisrv/projects/project-id')
        self.assertEqual(calls[0].request.method, 'DELETE')
