from typing import Generator, List, Union

from alteia.apis.provider import AuthAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId


class UsersImpl:
    def __init__(self, auth_api: AuthAPI, **kwargs):
        self._provider = auth_api

    def describe(self, user: ResourceId = None, **kwargs) -> Resource:
        """Describe a user.

        Args:
            user: User identifier to describe.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            User : User resource.

        """
        data = kwargs

        if user:
            data['user'] = user

        content = self._provider.post(path='describe-user', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search users.

        Args:
            filter: Search filter (refer to
                ``/search-users`` definition in the User
                and company management API for a detailed description
                of supported operators).

            limit: Maximum number of results to extract.

            page: Page number (starting at page 1).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resources: A list of resources OR a namedtuple
                with total number of results and list of resources.

        """
        return search(
            self,
            url='search-users',
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
        """Return a generator to search through users.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found users are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 1).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found users.

        """
        return search_generator(self, first_page=1, filter=filter, limit=limit,
                                page=page, **kwargs)
