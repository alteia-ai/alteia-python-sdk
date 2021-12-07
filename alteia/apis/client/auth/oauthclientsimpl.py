from datetime import datetime
from typing import Generator, List, Union

from alteia.apis.provider import AuthAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId


class OAuthClientsImpl:
    def __init__(self, auth_api: AuthAPI, **kwargs):
        self._provider = auth_api

    def create(self, name: str, *, client_type='sdk',
               expiration_date: datetime = None, **kwargs) -> Resource:
        """Create an OAuth client.

        This client will be used to generate a temporary connection
        token.

        Args:
            name: OAuth client name.

            client_type: Client type (only `sdk` is supported).

            expiration_date: Optional expiration date.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource for the client created.

        """
        data = kwargs
        data.update({
            'name': name,
            'client_type': client_type,
        })

        if expiration_date is not None:
            data['expiration_date'] = expiration_date

        desc = self._provider.post(path='create-client', data=data)
        return Resource(**desc)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search OAuth clients.

        Args:
            filter: Search filter dictionary.

            limit: Maximum number of results to extract.

            page: Page number (starting at page 1).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found

        Returns:
            A list of resources or a namedtuple with total number of
            results and list of resources.

        """
        return search(
            self,
            url='search-clients',
            filter=filter,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through OAuth clients.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found OAuth clients are sorted chronologically in order to
        allow new resources to be found during the search.

        Args:
            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            page: Optional page number to start the search at (default is 1).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding resources for found OAuth clients.

        """
        return search_generator(self, first_page=1, filter=filter, limit=limit,
                                page=page, **kwargs)

    def delete(self, client: ResourceId, **kwargs) -> Resource:
        """Delete an OAuth client.

        Args:
            client: Identifier of OAuth client to delete.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Deleted resource.

        """
        data = kwargs
        data['client'] = client
        desc = self._provider.post(path='delete-client', data=data)
        return Resource(**desc)
