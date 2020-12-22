from typing import Generator

from alteia.core.resources.resource import Resource


def search_generator(manager, *,
                     page: int = None, first_page: int,
                     filter: dict = None, limit: int = 50,
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
    for name, value in [('filter', filter),
                        ('page', first_page if page is None else page),
                        ('sort', {'creation_date': 1}),
                        ('limit', limit)]:
        if value is not None:
            data[name] = value

    resources = None
    while resources is None or len(resources) > 0:
        resources = manager.search(**data)
        for resource in resources:
            yield resource

        data['page'] += 1
