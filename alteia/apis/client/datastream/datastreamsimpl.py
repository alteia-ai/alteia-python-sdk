"""
    Datastreams implementation
"""

from typing import Dict, Generator, List, Union

from alteia.apis.provider import DataflowServiceAPI
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import Resource, ResourceId


class DatastreamsImpl:
    def __init__(self, dataflow_service_api: DataflowServiceAPI, **kwargs):
        self._provider = dataflow_service_api

    def create(
        self,
        *,
        name: str,
        start_date: str,
        end_date: str,
        source: Dict,
        template: ResourceId,
        **kwargs
    ) -> Resource:
        """Create a datastream.

        Args:
            name: Datastream name.

            start_date: date-time.

            end_date: date-time.

            source: Storage source.

            template: Datastream template identifier.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created datastream description.

        Examples:
            >>> sdk.datastream.create(
            ...     name="My datastream",
            ...     start_date="2023-01-01T05:00:00.000Z",
            ...     end_date="2023-02-01T05:00:00.000Z",
            ...     source={
            ...         "url": "s3://myBucket/prefix/",
            ...         "regex": ".*las",
            ...         "synchronisation": {
            ...             "type": "on_trigger"
            ...         }
            ...     },
            ...     template="633d561201a94aa267559524"
            ...     description="Description"
            ... )
            Resource(_id='5e5155ae8dcb064fcbf4ae35')

        """
        data: Dict = kwargs

        data.update(
            {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "source": source,
                "template": template,
            }
        )

        desc = self._provider.post(path="create-datastream", data=data)

        return Resource(**desc)

    def search(
        self,
        *,
        filter: Dict = None,
        limit: int = None,
        page: int = None,
        sort: dict = None,
        return_total: bool = False,
        **kwargs
    ) -> Union[ResourcesWithTotal, List[Resource]]:

        """Search for a list of datastreams.

        Args:
            filter: Search filter dictionary (refer to ``/search-datastreams``
                definition in the Dataflow Service API for a detailed
                description of ``filter``).

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 0).

            sort: Optional Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A list of datastream resources OR a namedtuple
                with total number of results and list of datastream resources.

        """
        data = kwargs

        for prop_name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
        ]:
            if value is not None:
                data.update({prop_name: value})

        search_desc = self._provider.post(
            path="search-datastreams", data=data, as_json=True
        )

        datastreams = search_desc.get("results")

        results = [Resource(**datastream) for datastream in datastreams]

        if return_total:
            total = search_desc.get("total")
            return ResourcesWithTotal(total=total, results=results)

        return results

    def search_generator(
        self, *, filter: dict = None, limit: int = 50, page: int = None, **kwargs
    ) -> Generator[Resource, None, None]:
        """Return a generator to search through datastreams.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found datastreams are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 1).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found datastreams.

        """
        return search_generator(
            self, first_page=1, filter=filter, limit=limit, page=page, **kwargs
        )

    def describe(self, *, datastream: ResourceId) -> Resource:
        """Describe a datastream.

        Args:
            datastream: Identifier of the datastream to describe.

        Returns:
            The datastream description.

        """

        data: Dict = dict(datastream=datastream)
        desc = self._provider.post(path="describe-datastream", data=data)

        return Resource(**desc)

    def delete(self, datastream: ResourceId) -> None:
        """Delete a datastream entry.

        Args:
            datastream: datastream identifier.

        """

        data: Dict = dict(datastream=datastream)
        self._provider.post(path="delete-datastream", data=data, as_json=False)
