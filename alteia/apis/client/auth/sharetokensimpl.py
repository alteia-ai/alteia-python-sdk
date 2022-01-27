import logging
from typing import Generator, List, Union

from alteia.apis.provider import AuthAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId

LOGGER = logging.getLogger(__name__)


class ShareTokensImpl:
    def __init__(self, auth_api: AuthAPI, sdk, **kwargs):
        self._provider = auth_api
        self._sdk = sdk

    def create(self, dataset: Union[ResourceId,
                                    List[ResourceId]], *,
               duration: int = None,
               **kwargs) -> Resource:
        """Create a share token for a given dataset.

        Share token creation is restricted to users with admin profile
        or a manager role on their company.

        When sharing multiple datasets, all datasets are expected to
        belong to a single company.

        Args:
            dataset: Dataset identifier or list of dataset identifiers
                to create a share token for.

            duration: Optional duration in seconds of the created
                token. When equal to ``None`` (the default) the
                created token won't expire.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Dictionary with ``token``, ``expiration_date`` and
            ``scope`` keys.

        Example:
            >>> desc = sdk.share_tokens.create('5d08ebe86a17271b23bc0fcd')
            >>> desc.token[:16]
            'YfkX6oB5JB02L9x5'

        """
        data = kwargs
        if isinstance(dataset, list):
            dataset_ids = dataset
        else:
            dataset_ids = [dataset]

        data.update({'scope': {'datasets': dataset_ids}})

        datasets = self._sdk.datasets.describe(
            dataset_ids,
            fields={'include': ['company']})
        company_ids = set([d.company for d in datasets])
        if len(company_ids) != 1:
            raise RuntimeError('Expecting datasets in a single company')

        data['company'] = list(company_ids)[0]

        if duration is not None:
            data['duration'] = duration

        desc = self._provider.post(path='/create-share-token', data=data)
        return Resource(**desc)

    def revoke(self, token: str, **kwargs):
        """Revoke a share token.

        Share token revocation is restricted to users with admin
        profile or a manager role on their company.

        Args:
            token: Token to revoke.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'token': token})

        self._provider.post(path='/revoke-share-token', data=data,
                            as_json=False)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search share tokens.

        Share token search is restricted to users with admin profile
        or a manager role on their company.

        Args:
            filter: Search filter (refer to ``/search-share-tokens``
                definition in the Authentication API specification for
                a detailed description of supported operators).

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 1).

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

        Returns:
            List of share token resources (with ``token``, ``expiration_date`` and ``scope`` keys)
            or a namedtuple with total number of results and the list of resources.

        """

        # sort is not supported yet
        if kwargs.get('sort') is not None:
            kwargs.pop('sort')

        return search(
            self,
            url='search-share-tokens',
            filter=filter,
            limit=limit,
            page=page,
            return_total=return_total,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through share tokens.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found share tokens are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 1).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found share tokens.

        """
        # sort is not supported yet
        if kwargs.get('sort') is not None:
            kwargs.pop('sort')

        return search_generator(self, first_page=1, filter=filter, limit=limit,
                                page=page, **kwargs)
