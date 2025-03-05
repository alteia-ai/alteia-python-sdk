import json
from urllib.parse import parse_qs, urlparse

from alteia.core.errors import ParameterError
from tests.core.resource_test_base import ResourcesTestBase
from tests.url_mock import Responses

responses = Responses()

COMMENT_CREATION_RESP_BODY = """
    {
        "comment": {
            "_id": "comment-id",
            "project_id": "project-id",
            "target": {
                "type": "dataset",
                "id": "ds-id"
            },
            "text": "my comment",
            "author": {
                "id": "user-id",
                "displayName": "User Name"
            },
            "date": "2019-12-25T00:00:00.000Z",
            "read_by": []
        }
    }
    """

PHOTO_COMMENT_CREATION_RESP_BODY = """
    {
        "comment": {
            "_id": "comment-id",
            "project_id": "project-id",
            "target": {
                "type": "photo",
                "id": "flight-id",
                "subId": "ds-id"
            },
            "text": "my photo comment",
            "author": {
                "id": "user-id",
                "displayName": "User Name"
            },
            "date": "2019-12-25T00:00:00.000Z",
            "read_by": []
        }
    }
    """

SEARCH_COMMENTS_RESP_BODY = """
    {
        "conversations": [
            {
                "_id": {
                    "type": "photo",
                    "id": "flight-id",
                    "subId": "ds-id"
                },
                "comments": [
                    {
                        "_id": "comment-id",
                        "text": "my photo comment",
                        "author": {
                            "id": "user-id",
                            "displayName": "User Name"
                        },
                        "date": "2019-12-25T00:00:00.000Z"
                    }
                ],
                "participants": 1,
                "unreadComments": 0,
                "lastUpdate": "2019-12-25T01:00:00.000Z"
            }
        ]
    }
    """

MARK_AS_READ_BODY = ""


class TestComments(ResourcesTestBase):
    """Test comments."""

    @responses.activate
    def test_create(self):
        responses.add(
            "POST",
            "/project-manager/comments",
            body=COMMENT_CREATION_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        self.sdk.comments.create(text="my comment", project="project-id", type="dataset", target="ds-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/comments")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)

        self.assertEqual(
            request_body,
            {
                "project_id": "project-id",
                "target": {"type": "dataset", "id": "ds-id"},
                "text": "my comment",
            },
        )

    @responses.activate
    def test_create_photo_comment(self):
        responses.add(
            "POST",
            "/project-manager/comments",
            body=PHOTO_COMMENT_CREATION_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        comment = self.sdk.comments.create(
            text="my photo comment",
            project="project-id",
            type="photo",
            target="ds-id",
            flight="flight-id",
        )

        assert comment.id == "comment-id"
        assert comment.project == "project-id"
        assert comment.type == "photo"
        assert comment.flight == "flight-id"
        assert comment.target == "ds-id"
        assert comment.text == "my photo comment"
        assert comment.creation_user == "user-id"
        assert comment.creation_date == "2019-12-25T00:00:00.000Z"

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/comments")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)

        self.assertEqual(
            request_body,
            {
                "project_id": "project-id",
                "target": {"type": "photo", "id": "flight-id", "subId": "ds-id"},
                "text": "my photo comment",
            },
        )

    def test_create_photo_comment_without_flight(self):
        with self.assertRaises(ParameterError):
            self.sdk.comments.create(
                text="my photo comment",
                project="project-id",
                type="photo",
                target="ds-id",
            )

    def test_create_photo_comment_without_target(self):
        with self.assertRaises(ParameterError):
            self.sdk.comments.create(
                text="my photo comment",
                project="project-id",
                type="photo",
                flight="flight-id",
            )

    @responses.activate
    def test_search_comments(self):
        responses.add(
            "GET",
            "/project-manager/comments",
            body=SEARCH_COMMENTS_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        found_comments = self.sdk.comments.search(project="project-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        assert len(found_comments) == 1
        comment = found_comments[0]

        assert comment.id == "comment-id"
        assert comment.project == "project-id"
        assert comment.type == "photo"
        assert comment.flight == "flight-id"
        assert comment.target == "ds-id"
        assert comment.text == "my photo comment"
        assert comment.creation_user == "user-id"
        assert comment.creation_date == "2019-12-25T00:00:00.000Z"

        self.assertEqual(calls[0].request.url, "/project-manager/comments?project_id=project-id")
        self.assertEqual(calls[0].request.method, "GET")

    @responses.activate
    def test_search_photo_comments(self):
        responses.add(
            "GET",
            "/project-manager/comments",
            body=SEARCH_COMMENTS_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        self.sdk.comments.search(project="project-id", type="photo", target="ds-id", flight="flight-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        url = calls[0].request.url
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)  # {'project_id': ['project-id']}
        query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        self.assertEqual(calls[0].request.method, "GET")
        self.assertEqual(
            query_params,
            {
                "project_id": "project-id",
                "target_type": "photo",
                "target_id": "flight-id",
                "target_subid": "ds-id",
            },
        )

    @responses.activate
    def test_mark_comment_as_read(self):
        responses.add(
            "POST",
            "/project-manager/comments/mark-as-read",
            body=MARK_AS_READ_BODY,
            status=200,
            content_type="text/plain",
        )

        self.sdk.comments.mark_as_read(project="project-id", type="dataset", target="ds-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/comments/mark-as-read")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)

        self.assertEqual(
            request_body,
            {"project_id": "project-id", "target": {"type": "dataset", "id": "ds-id"}},
        )
