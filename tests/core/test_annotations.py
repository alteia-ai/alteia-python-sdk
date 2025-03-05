import json

from tests.core.resource_test_base import ResourcesTestBase
from tests.url_mock import Responses

responses = Responses()


class TestAnnotations(ResourcesTestBase):
    """Test annotations."""

    @responses.activate
    def test_search(self):
        responses.add(
            "POST",
            "/map-service/annotations/search-annotations",
            body=json.dumps({"results": [{"_id": "annotation-id"}]}),
            status=200,
            content_type="application/json",
        )

        self.sdk.annotations.search(project="project-id")

        calls = responses.calls
        self.assertEqual(len(calls), 1)

        self.assertEqual(calls[0].request.url, "/map-service/annotations/search-annotations")
        self.assertEqual(calls[0].request.method, "POST")

        request_body = json.loads(calls[0].request.body)
        self.assertEqual(request_body["filter"], {"project": {"$eq": "project-id"}})
