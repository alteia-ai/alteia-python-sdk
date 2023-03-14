"""
    Datastreams files implementation
"""

from typing import Dict, Generator, List, Union

from alteia.apis.provider import DataflowServiceAPI
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import Resource


class DatastreamsFilesImpl:
    def __init__(self, dataflow_service_api: DataflowServiceAPI, **kwargs):
        self._provider = dataflow_service_api

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

        """Search for a list of datastream files.

        Args:
            filter: Search filter dictionary (refer to ``/search-datastreams-files``
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
            A list of datastream files resources OR a namedtuple
                with total number of results and list of datastream files resources.

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
            path="search-datastreams-files", data=data, as_json=True
        )

        datastream_files = search_desc.get("results")

        results = [Resource(**datastream_file) for datastream_file in datastream_files]

        if return_total:
            total = search_desc.get("total")
            return ResourcesWithTotal(total=total, results=results)

        return results

    def search_generator(
        self, *, filter: dict = None, limit: int = 50, page: int = None, **kwargs
    ) -> Generator[Resource, None, None]:
        """Return a generator to search through datastream files.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found datastream files are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 1).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found datastream files.

        """
        return search_generator(
            self, first_page=1, filter=filter, limit=limit, page=page, **kwargs
        )
