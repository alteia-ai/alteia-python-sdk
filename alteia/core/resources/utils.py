import copy
import warnings
from typing import Generator, List, Union

from alteia.core.resources.resource import Resource, ResourcesWithTotal


def search(manager, *, url: str, filter: dict = None, limit: int = None,
           page: int = None, sort: dict = None, return_total: bool = False,
           **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
    """Generic search function.

    Args:
        manager: Resource manager.

        url: URL for the search request.

        filter: Search filter dictionary.

        limit: Maximum number of results to extract.

        page: Page number (starting at page 1).

        sort: Sort the results on the specified attributes
            (``1`` is sorting in ascending order,
            ``-1`` is sorting in descending order).

        return_total: Return the number of results found.

        **kwargs: Optional keyword arguments. Those arguments are
            passed as is to the API provider.

    Returns:
        A list of resource descriptions or a namedtuple with
        total number of results and list of resource descriptions.

    """
    data = kwargs
    for name, value in [('filter', filter or {}),
                        ('limit', limit),
                        ('page', page),
                        ('sort', sort)]:
        if value is not None:
            data.update({name: value})

    r = manager._provider.post(url, data=data)

    descriptions = r.get('results')

    results = [Resource(**desc) for desc in descriptions]

    if return_total is True:
        total = r.get('total')
        return ResourcesWithTotal(total=total, results=results)
    else:
        return results


def search_generator(manager, *,
                     page: int = None, first_page: int,
                     filter: dict = None, limit: int = 50,
                     keyset_pagination: bool = False,
                     **kwargs) -> Generator[Resource, None, None]:
    """Return a generator to search through the given manager resources.

    The generator allows the user not to care about the pagination of
    results, while being memory-effective.

    Found resources are sorted chronologically in order to allow
    new resources to be found during the search.

    Args:
        manager: Resource manager.

        first_page: page number of first page, usually 1 or 0
            depending on the underlying API.

        page: Optional page number to start the search at (default is `first_page`).

        filter: Search filter dictionary.

        limit: Optional maximum number of results by search
            request (default to 50).

        **kwargs: Optional keyword arguments. Those arguments are
            passed as is to the API provider.

    Returns:
        A generator yielding found resources.

    """
    if not hasattr(manager, 'search'):
        raise RuntimeError('Search action not found on manager {!r}'.format(manager))

    data = kwargs
    if page is not None:
        warnings.warn("Keyset pagination disabled due to explicit starting page")
        keyset_pagination = False

    if keyset_pagination and 'sort' in data:
        warnings.warn("Keyset pagination disabled due to custom sort")
        keyset_pagination = False

    if keyset_pagination and filter and '_id' in filter.keys():
        warnings.warn("Keyset pagination disabled due to custom _id filter")
        keyset_pagination = False

    if keyset_pagination:
        data['sort'] = {'_id': -1}
        if limit is not None:
            data['limit'] = limit

        f = copy.copy(filter) if filter else dict()

        def next_filter(resources):
            if resources is None:
                return filter

            if len(resources) == 0:
                return None

            min_id = resources[-1].id
            f['_id'] = {'$lt': min_id}
            return f
    else:
        for name, value in [('page', first_page if page is None else page),
                            ('sort', {'_id': 1}),
                            ('limit', limit)]:
            if value is not None:
                data[name] = value

        def next_filter(resources):
            return filter

    resources = None
    while resources is None or len(resources) > 0:
        resources = manager.search(filter=next_filter(resources), **data)
        for resource in resources:
            yield resource

        if not keyset_pagination:
            data['page'] += 1
