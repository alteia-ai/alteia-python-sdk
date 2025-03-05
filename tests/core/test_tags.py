import json
from urllib.parse import parse_qs, urlparse

from alteia.core.errors import ParameterError
from alteia.core.resources.tags import Tag
from tests.core.resource_test_base import ResourcesTestBase
from tests.url_mock import Responses

responses = Responses()

TAG_CREATION_RESP_BODY = """
    {
        "tag": {
            "_id": "tag-id",
            "project_id": "project-id",
            "target": {
                "type": "dataset",
                "id": "ds-id"
            },
            "text": "my tag",
            "author": {
                "id": "user-id",
                "displayName": "User Name"
            },
            "date": "2019-12-25T00:00:00.000Z"
        }
    }
    """

PHOTO_TAG_CREATION_RESP_BODY = """
    {
        "tag": {
            "_id": "tag-id",
            "project_id": "project-id",
            "target": {
                "type": "photo",
                "id": "flight-id",
                "subId": "ds-id"
            },
            "text": "my photo tag",
            "author": {
                "id": "user-id",
                "displayName": "User Name"
            },
            "date": "2019-12-25T00:00:00.000Z"
        }
    }
    """

SEARCH_TAGS_RESP_BODY = """
    {
        "tagGroups": [
            {
                "_id": {
                    "type": "photo",
                    "id": "flight-id",
                    "subId": "ds-id"
                },
                "tags": [
                    {
                        "_id": "tag-id",
                        "author": {
                            "id": "user-id",
                            "displayName": "User Name"
                        },
                        "date": "2019-12-25T00:00:00.000Z",
                        "text": "my photo tag"
                    }
                ]
            }
        ]
    }
    """

TAG_DELETION_RESP_BODY = """
    {
        "tag": {
            "_id": "tag-id",
            "project_id": "project-id",
            "target": {
                "type": "photo",
                "id": "flight-id",
                "subId": "ds-id"
            },
            "text": "my photo tag",
            "author": {
                "id": "user-id",
                "displayName": "User Name"
            },
            "date": "2019-12-25T00:00:00.000Z",
            "deleted": "2019-12-25T00:00:00.000Z",
            "deleted_by": {
                "id": "deletion-user-id",
                "displayName": "Deletion User"
            }
        }
    }
    """


class TestTags(ResourcesTestBase):
    """Test tags."""

    @responses.activate
    def test_create(self):
        responses.add(
            "POST",
            "/project-manager/tags",
            body=TAG_CREATION_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        tag = self.sdk.tags.create(name="my tag", project="project-id", type="dataset", target="ds-id")

        assert tag.id == "tag-id"
        assert tag.project == "project-id"
        assert tag.type == "dataset"
        assert tag.target == "ds-id"
        assert tag.flight is None
        assert tag.name == "my tag"
        assert tag.creation_user == "user-id"
        assert tag.creation_date == "2019-12-25T00:00:00.000Z"

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/tags")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)

        self.assertEqual(
            request_body,
            {
                "project_id": "project-id",
                "target": {"type": "dataset", "id": "ds-id"},
                "text": "my tag",
            },
        )

    @responses.activate
    def test_create_photo_tag(self):
        responses.add(
            "POST",
            "/project-manager/tags",
            body=PHOTO_TAG_CREATION_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        tag = self.sdk.tags.create(
            name="my photo tag",
            project="project-id",
            type="photo",
            target="ds-id",
            flight="flight-id",
        )

        assert tag.id == "tag-id"
        assert tag.project == "project-id"
        assert tag.type == "photo"
        assert tag.target == "ds-id"
        assert tag.flight == "flight-id"
        assert tag.name == "my photo tag"
        assert tag.creation_user == "user-id"
        assert tag.creation_date == "2019-12-25T00:00:00.000Z"

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/tags")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)

        self.assertEqual(
            request_body,
            {
                "project_id": "project-id",
                "target": {"type": "photo", "id": "flight-id", "subId": "ds-id"},
                "text": "my photo tag",
            },
        )

    def test_create_photo_tag_without_flight(self):
        with self.assertRaises(ParameterError):
            self.sdk.tags.create(name="my photo tag", project="project-id", type="photo", target="ds-id")

    def test_create_photo_tag_without_target(self):
        with self.assertRaises(ParameterError):
            self.sdk.tags.create(
                name="my photo tag",
                project="project-id",
                type="photo",
                flight="flight-id",
            )

    @responses.activate
    def test_search_tags(self):
        responses.add(
            "GET",
            "/project-manager/tags",
            body=SEARCH_TAGS_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        found_tags = self.sdk.tags.search(project="project-id")
        assert len(found_tags) == 1
        tag = found_tags[0]

        assert tag.id == "tag-id"
        assert tag.project == "project-id"
        assert tag.type == "photo"
        assert tag.target == "ds-id"
        assert tag.flight == "flight-id"
        assert tag.name == "my photo tag"
        assert tag.creation_user == "user-id"
        assert tag.creation_date == "2019-12-25T00:00:00.000Z"

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/tags?project_id=project-id")
        self.assertEqual(calls[0].request.method, "GET")

    @responses.activate
    def test_search_photo_tags(self):
        responses.add(
            "GET",
            "/project-manager/tags",
            body=SEARCH_TAGS_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        found_tags = self.sdk.tags.search(project="project-id", type="photo", target="ds-id", flight="flight-id")

        assert len(found_tags) == 1

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
    def test_delete_tags(self):
        responses.add(
            "DELETE",
            "/project-manager/tags/tag-id",
            body=TAG_DELETION_RESP_BODY,
            status=200,
            content_type="application/json",
        )

        self.sdk.tags.delete(tag="tag-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/project-manager/tags/tag-id")
        self.assertEqual(calls[0].request.method, "DELETE")

    def test_convert_uisrv_desc_to_Tag(self):
        uisrv_desc = json.loads(TAG_CREATION_RESP_BODY).get("tag")
        tag = self.sdk.tags._convert_uisrv_desc_to_Tag(desc=uisrv_desc)
        assert (
            tag.__dict__
            == Tag(
                id="tag-id",
                project="project-id",
                target="ds-id",
                type="dataset",
                name="my tag",
                creation_user="user-id",
                creation_date="2019-12-25T00:00:00.000Z",
            ).__dict__
        )

    def test_convert_uisrv_desc_to_Tag_deleted(self):
        uisrv_desc = json.loads(TAG_DELETION_RESP_BODY).get("tag")
        tag = self.sdk.tags._convert_uisrv_desc_to_Tag(desc=uisrv_desc)
        assert (
            tag.__dict__
            == Tag(
                id="tag-id",
                project="project-id",
                target="ds-id",
                type="photo",
                name="my photo tag",
                flight="flight-id",
                creation_user="user-id",
                creation_date="2019-12-25T00:00:00.000Z",
                deletion_user="deletion-user-id",
                deletion_date="2019-12-25T00:00:00.000Z",
            ).__dict__
        )
