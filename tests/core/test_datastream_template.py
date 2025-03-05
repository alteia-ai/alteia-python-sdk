import json
from copy import deepcopy

from tests.core.resource_test_base import ResourcesTestBase
from tests.url_mock import Responses

responses = Responses()

DATA_CREATE = {
    "description": "description",
    "aggregate": {"type": "", "parameters": {}, "strategy": {}},
    "company": "507f191e810c19729de860eb",
}

CONTEXTUALISATION = {
    "type": "geographic",
    "parameters": {
        "assets_schema_repository": "XXX",
        "assets_schema": "",
        "geographic_buffer": 50,
    },
}
TRANSFORM = {
    "analytic": {
        "name": "datastream",
        "version_range": "XXX YYY",
        "inputs_mapping": {},
        "parameters": {},
        "outputs_mapping": "",
    },
}

DATA_RESULT = {
    "name": "My datastream",
    "description": "string",
    "source": "object-storage",
    "import": {"dataset_parameters": {}},
    "aggregate": {
        "type": "string",
        "parameters": {},
        "strategy": {},
    },
    "company": "5b8e79dccec9d16607e0955f",
    "_id": "5b8e79dccec9d16607e0955f",
    "creation_user": "5b8e79dccec9d16607e0955f",
    "creation_date": "2022-09-27T14:09:55.691Z",
    "modification_user": "5b8e79dccec9d16607e0955f",
    "modification_date": "2022-09-27T14:09:55.691Z",
    "deletion_user": "5b8e79dccec9d16607e0955f",
    "deletion_date": "2022-09-27T14:09:55.691Z",
}


class TestDatastreamTemplate(ResourcesTestBase):
    @staticmethod
    def __legacy_search():
        return json.dumps(
            {
                "total": 1,
                "results": [DATA_RESULT],
            }
        )

    @staticmethod
    def __legacy_create_no_contextualisation_and_transform():
        return json.dumps(DATA_RESULT)

    @staticmethod
    def __legacy_create_with_contextualisation():
        DATA_RESULT["contextualisation"] = CONTEXTUALISATION
        return json.dumps(DATA_RESULT)

    @staticmethod
    def __legacy_create_with_transform():
        DATA_RESULT["transform"] = TRANSFORM
        return json.dumps(DATA_RESULT)

    @staticmethod
    def __legacy_create():
        DATA_RESULT["contextualisation"] = CONTEXTUALISATION
        DATA_RESULT["transform"] = TRANSFORM
        return json.dumps(DATA_RESULT)

    @staticmethod
    def __legacy_describe():
        return json.dumps(DATA_RESULT)

    @staticmethod
    def __legacy_describes():
        return json.dumps([DATA_RESULT])

    @responses.activate
    def test_datastream_template_create(self):
        data_create = deepcopy(DATA_CREATE)
        data_create.update({"contextualisation": CONTEXTUALISATION, "transform": TRANSFORM})
        responses.add(
            "POST",
            "/dataflow/create-datastream-template",
            body=self.__legacy_create(),
            status=200,
            content_type="application/json",
        )

        calls = responses.calls
        self.sdk.datastreamtemplates.create(
            name="My datastream",
            import_dataset={"dataset_parameters": {}},
            source={"type": "object-storage"},
            **data_create,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/create-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"description": "description", "aggregate": {"type": "", "parameters": {}, "strategy": {}},'
            ' "company": "507f191e810c19729de860eb", "contextualisation": {"type": "geographic", "parameters":'
            ' {"assets_schema_repository": "XXX", "assets_schema": "", "geographic_buffer": 50}},'
            ' "transform": {"analytic": {"name": "datastream", "version_range": "XXX YYY",'
            ' "inputs_mapping": {}, "parameters": {}, "outputs_mapping": ""}}, "name": "My datastream",'
            ' "source": {"type": "object-storage"}, "import": {"dataset_parameters": {}}}',
        )

    @responses.activate
    def test_datastream_template_create_with_contextualisation_without_transfrom(self):
        data_create = deepcopy(DATA_CREATE)
        data_create.update({"contextualisation": CONTEXTUALISATION})

        responses.add(
            "POST",
            "/dataflow/create-datastream-template",
            body=self.__legacy_create_with_contextualisation(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.create(
            name="My datastream",
            import_dataset={"dataset_parameters": {}},
            source={"type": "object-storage"},
            **data_create,
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/create-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"description": "description", "aggregate": {"type": "", "parameters": {}, "strategy": {}},'
            ' "company": "507f191e810c19729de860eb", "contextualisation": {"type": "geographic",'
            ' "parameters": {"assets_schema_repository": "XXX", "assets_schema": "", "geographic_buffer": 50}},'
            ' "name": "My datastream", "source": {"type": "object-storage"}, "import": {"dataset_parameters": {}}}',
        )

    @responses.activate
    def test_datastream_template_create_with_transform_without_contextualisation(self):
        data_create = deepcopy(DATA_CREATE)
        data_create.update({"transform": TRANSFORM})
        responses.add(
            "POST",
            "/dataflow/create-datastream-template",
            body=self.__legacy_create_with_transform(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.create(
            name="My datastream",
            import_dataset={"dataset_parameters": {}},
            source={"type": "object-storage"},
            **data_create,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/create-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"description": "description", "aggregate": {"type": "", "parameters": {}, "strategy": {}},'
            ' "company": "507f191e810c19729de860eb", "transform": {"analytic": {"name": "datastream",'
            ' "version_range": "XXX YYY", "inputs_mapping": {}, "parameters": {}, "outputs_mapping": ""}},'
            ' "name": "My datastream", "source": {"type": "object-storage"}, "import": {"dataset_parameters": {}}}',
        )

    @responses.activate
    def test_datastream_template_create_without_transform_nor_contextualisation(self):
        responses.add(
            "POST",
            "/dataflow/create-datastream-template",
            body=self.__legacy_create_no_contextualisation_and_transform(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.create(
            name="My datastream",
            import_dataset={"dataset_parameters": {}},
            source={"type": "object-storage"},
            **DATA_CREATE,
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/create-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"description": "description", "aggregate": {"type": "", "parameters": {}, "strategy": {}},'
            ' "company": "507f191e810c19729de860eb", "name": "My datastream", "source":'
            ' {"type": "object-storage"}, "import": {"dataset_parameters": {}}}',
        )

    @responses.activate
    def test_datastream_template_search(self):
        responses.add(
            "POST",
            "/dataflow/search-datastream-templates",
            body=self.__legacy_search(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.search(
            filter={
                "company": {"$eq": "507f191e810c19729de860eb"},
                "name": {"$match": "My datastream"},
            },
            limit=100,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/search-datastream-templates")
        self.assertEqual(
            calls[0].request.body,
            '{"filter": {"company": {"$eq": "507f191e810c19729de860eb"},'
            ' "name": {"$match": "My datastream"}}, "limit": 100}',
        )

    @responses.activate
    def test_datastream_template_delete(self):
        responses.add(
            "POST",
            "/dataflow/delete-datastream-template",
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.delete(
            template="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/delete-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"datastreamtemplate": "507f191e810c19729de860eb"}',
        )

    @responses.activate
    def test_datastream_template_describe(self):
        responses.add(
            "POST",
            "/dataflow/describe-datastream-template",
            body=self.__legacy_describe(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.describe(
            template="507f191e810c19729de860eb",
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/describe-datastream-template")
        self.assertEqual(
            calls[0].request.body,
            '{"datastreamtemplate": "507f191e810c19729de860eb"}',
        )

    @responses.activate
    def test_datastream_template_describes(self):
        responses.add(
            "POST",
            "/dataflow/describe-datastream-templates",
            body=self.__legacy_describes(),
            status=200,
            content_type="application/json",
        )
        calls = responses.calls
        self.sdk.datastreamtemplates.describes(
            templates=["507f191e810c19729de860eb"],
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, "/dataflow/describe-datastream-templates")
        self.assertEqual(
            calls[0].request.body,
            '{"datastreamtemplates": ["507f191e810c19729de860eb"]}',
        )
