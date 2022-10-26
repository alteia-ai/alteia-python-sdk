from typing import Dict, List, Union

from alteia.apis.provider import DataflowServiceAPI
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.utils.typing import Resource, ResourceId


class DatastreamTemplateImpl:
    def __init__(self, dataflow_service_api: DataflowServiceAPI, **kwargs):
        self._provider = dataflow_service_api

    def create(
        self,
        *,
        name: str,
        source: Dict,
        import_dataset: Dict,
        contextualisation: Dict,
        transform: Dict,
        **kwargs
    ) -> Resource:
        """Create a datastream template.

        Args:
            name: Datastream name.

            source: Storage source.

            import_dataster: dataset paramter.

            contextualisation: contextualisation.

            transform: transform.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created datastream description.

        Examples:
            >>> sdk.datastream.create(
            ...     name="My datastream",
            ...     source= "object-storage",
            ...     import_dataset= {"dataset_parameters": {}},
            ...     contextualisation= {
            ...         "type": "geographic",
            ...          "parameters": {
            ...             "assets_schema_repository": "XXX",
            ...             "assets_schema": "",
            ...             "geographic_buffer": 50,
            ...          },
            ...     },
            ...     "description": "My datastream description",
            ...     "transform": {
            ...         "analytic": {
            ...             "name": "datastream",
            ...             "version_range": "XXX YYY",
            ...             "inputs_mapping": {},
            ...             "parameters": {},
            ...             "outputs_mapping": "",
            ...         },
            ...      },
            ...     "aggregate": {"type": "", "parameters": {}, "strategy": {}},
            ...     "company": "XXX"
            ... )
            Resource(_id='5e5155ae8dcb064fcbf4ae35')

        """
        data: Dict = kwargs

        data.update(
            {
                "name": name,
                "source": source,
                "import": import_dataset,
                "contextualisation": contextualisation,
                "transform": transform,
            }
        )

        desc = self._provider.post(path="create-datastream-template", data=data)

        return Resource(**desc)

    def delete(self, template: ResourceId) -> None:
        """Delete a datastream entry.

        Args:
            datastream: datastream identifier.

        """

        data: Dict = dict(datastreamtemplate=template)

        self._provider.post(path="delete-datastream-template", data=data, as_json=False)

    def search(
        self,
        *,
        filter: Dict = None,
        limit: int = None,
        page: int = None,
        sort: dict = None,
        exclude: List[str] = None,
        return_total: bool = False,
        **kwargs
    ) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search for a list of datastream.

        Args:
            company: Company id.

            filter: Search filter dictionary (refer to ``/search-datastream-templates``
                definition in the Datastream Service API for a detailed
                description of ``filter``).

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 0).

            sort: Optional Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            exclude: The properties to exclude art the response

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Datastream: A list of datastream resources OR a namedtuple
                with total number of results and list of datastream resources.

        """
        data = kwargs

        for prop_name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
            ("exlude", exclude),
        ]:
            if value is not None:
                data.update({prop_name: value})

        desc = self._provider.post(path="search-datastream-templates", data=data)

        datastream = desc.get("results")

        results = [Resource(**data) for data in datastream]

        if return_total:
            total = desc.get("total")
            return ResourcesWithTotal(total=total, results=results)

        return results

    def describe(self, *, template: ResourceId = None) -> Resource:
        """Describe an datastream template.

        Args:
            templates: Identifier of the datastream template to describe.

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

        Returns:
            The datastream template description.

        """

        data: Dict = dict(datastreamtemplate=template)

        desc = self._provider.post(path="describe-datastream-template", data=data)

        return Resource(**desc)

    def describes(self, *, templates: List[ResourceId] = None) -> List[Resource]:
        """Describe datastream templates.

        Args:
            templates: Identifier of the datastream templates to describe.

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

        Returns:
            Datastream: A list of datastream resources.

        """

        data: Dict = dict(datastreamtemplates=templates)

        desc = self._provider.post(path="describe-datastream-templates", data=data)

        return [Resource(**data) for data in desc]
