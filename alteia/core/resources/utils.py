import copy
import warnings
from typing import Dict, Generator, List, Optional, Union

from alteia.core.resources.resource import Resource, ResourcesWithTotal

ASCENDING = 1
DESCENDING = -1


def search(manager, *, url: str, filter: dict = None, fields: dict = None,
           limit: int = None, page: int = None,
           sort: dict = None, return_total: bool = False,
           **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
    """Generic search function.

    Args:
        manager: Resource manager.

        url: URL for the search request.

        filter: Optional Search filter dictionary.

        fields: Optional Field names to include or exclude from the response.
            `{"include: ["name", "creation_date"]}`
            `{"exclude: ["name", "creation_date"]}`
            Do not use both `include` and `exclude`.

        limit: Optional Maximum number of results to extract.

        page: Optional Page number (starting at page 1).

        sort: Optional. Sort the results on the specified attributes (``{"_id": 1}`` for example)
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
        A list of resource descriptions or a namedtuple with
        total number of results and list of resource descriptions.

    """
    data = kwargs
    for name, value in [('filter', filter or {}),
                        ('fields', fields),
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
                     filter: dict = None, fields: dict = None,
                     limit: int = 50, sort: Optional[Dict[str, int]] = None,
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

        filter: Optional Search filter dictionary.

        fields: Optional Field names to include or exclude from the response.
            `{"include: ["name", "creation_date"]}`
            `{"exclude: ["name", "creation_date"]}`
            Do not use both `include` and `exclude`.

        limit: Optional maximum number of results by search
            request (default to 50).

        sort: Optional. Sort the results on the specified attributes (``{"_id": 1}`` for example)
            (``1`` is sorting in ascending order,
            ``-1`` is sorting in descending order).

        keyset_pagination: Optional search using keyset pagination.


        **kwargs: Optional keyword arguments. Those arguments are
            passed as is to the API provider.

    Returns:
        A generator yielding found resources.

    """
    if not hasattr(manager, 'search'):
        raise RuntimeError(f'Search action not found on manager {manager!r}')

    data = kwargs
    if page is not None:
        warnings.warn("Keyset pagination disabled due to explicit starting page")
        keyset_pagination = False

    if fields is not None:
        data['fields'] = fields

    if keyset_pagination and sort:
        warnings.warn("Keyset pagination disabled due to custom sort")
        keyset_pagination = False

    if keyset_pagination and filter and '_id' in filter.keys():
        warnings.warn("Keyset pagination disabled due to custom _id filter")
        keyset_pagination = False

    if keyset_pagination:
        data['sort'] = {'_id': DESCENDING}
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
                            ('sort', sort or {'_id': ASCENDING}),
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
