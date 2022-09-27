import json

from urllib3_mock import Responses

from tests.core.resource_test_base import ResourcesTestBase

COLLECTION_TASK_RESPONSE = {
    "_id": "task-id-1",
    "name": "test task",
    "site": "1234",
    "survey": "5678",
    "status": "scheduled",
}

responses = Responses()


class TestCollectionTasks(ResourcesTestBase):
    @responses.activate
    def test_set_task_status(self):
        responses.add(
            "POST",
            "/dct-service/task/set-task-status",
            body=self.__search_single_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.collection_tasks.set_task_status("task-id-1", status="scheduled")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dct-service/task/set-task-status")
        self.assertEqual(
            calls[0].request.body, '{"task": "task-id-1", "status": "scheduled"}'
        )

    @responses.activate
    def test_describe_single_collection_task(self):
        responses.add(
            "POST",
            "/dct-service/task/describe-task",
            body=self.__search_single_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.collection_tasks.describe("task-id-1")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dct-service/task/describe-task")
        self.assertEqual(calls[0].request.body, '{"task": "task-id-1"}')

    @responses.activate
    def test_describe_multiple_collection_task(self):
        responses.add(
            "POST",
            "/dct-service/task/describe-tasks",
            body=self.__search_multiple_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.collection_tasks.describe(["task-id-1", "task-id-2"])

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dct-service/task/describe-tasks")
        self.assertEqual(calls[0].request.body, '{"tasks": ["task-id-1", "task-id-2"]}')

    @responses.activate
    def test_describe_multiple_collection_task_with_fields(self):
        responses.add(
            "POST",
            "/dct-service/task/describe-tasks",
            body=self.__search_multiple_post_response(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.collection_tasks.describe(
            ["task-id-1", "task-id-2"], fields={"include": ["requirement"]}
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dct-service/task/describe-tasks")
        self.assertEqual(
            calls[0].request.body,
            '{"fields": {"include": ["requirement"]}, "tasks": ["task-id-1", "task-id-2"]}',
        )

    @staticmethod
    def __search_single_post_response():
        return json.dumps(COLLECTION_TASK_RESPONSE)

    @staticmethod
    def __search_multiple_post_response():
        return json.dumps([COLLECTION_TASK_RESPONSE] * 2)
