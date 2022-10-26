"""Implementation of analytic configurations.

"""
from typing import Any, Dict, Generator, List, Union

from alteia.apis.provider import AnalyticsServiceAPI
from alteia.core.errors import QueryError
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds


class AnalyticConfigurationsImpl:
    def __init__(self, analytics_service_api: AnalyticsServiceAPI, **kwargs):
        self._provider = analytics_service_api

    def create(self,
               name: str,
               analytic_name: str,
               value: Dict[str, Any],
               analytic_version_range: str = '*',
               description: str = None,
               **kwargs) -> Resource:
        """Create a new configuration set for an analytic.

        Args:
            name: Configuration set name.

            analytic_name: Analytic name.

            value: Raw contents of the associated configuration.

            analytic_version_range: Optional version range of the analytic on
                which the configuration set can be applied (default: ``*``).

            description: Optional description.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            ResponseError: The creation response is incorrect.

        Returns:
            Resource: The created configuration set resource.

        """
        data = kwargs

        data.update({
            'name': name,
            'analytic_name': analytic_name,
        })

        if 'versions' not in data:  # can be set from kwargs
            data['versions'] = [{
                'analytic_version_range': analytic_version_range,
                'value': value,
            }]

        if description is not None:
            data['description'] = description

        desc = self._provider.post(path='create-analytic-configuration', data=data)
        return Resource(**desc)

    def describe(self, configuration_set: SomeResourceIds, **kwargs) -> Union[Resource, List]:
        """Describe an analytic configuration set or a list of analytic configuration sets.

        Args:
            configuration_set: Identifier of the configuration to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The configuration set resource or a list of configuration set resources.

        """
        data = kwargs
        if isinstance(configuration_set, list):
            results = []
            # the describe multiple is not available in the API, so do many simple describe
            for config_id in configuration_set:
                results.append(self.describe(config_id))

            # use these following lines when API will have the multiple describe:
            # ids_chunks = get_chunks(configuration, self._provider.max_per_describe)
            # for ids_chunk in ids_chunks:
            #     data['analytic_configurations'] = ids_chunk
            #     descs = self._provider.post('describe-analytic-configurations', data=data)
            #     results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['analytic_configuration'] = configuration_set
            desc = self._provider.post('describe-analytic-configuration', data=data)
            return Resource(**desc)

    def search(self, *, filter: dict = None, fields: dict = None, limit: int = 100,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search analytic configuration sets.

        Args:
            filter: Optional Search filter (refer to
                ``/search-analytic-configurations`` definition in the Analytic
                service API for a detailed description of supported operators).

            fields: Optional Field names to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            limit: Optional Maximum number of results to extract (default is ``100``).

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
             A list of resources OR a namedtuple
             with total number of results and list of resources.

        Examples:
            >>> # search configuration sets with name exactly equals to 'my config'
            >>> sdk.analytic_configurations.search(filter={'name': {'$eq': 'my config'}})
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]

            >>> # search configuration sets having 'my' in their name (case-insensitive)
            >>> sdk.analytic_configurations.search(filter={'name': {'$match': 'my'}})
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]

            >>> # search configuration sets by IDs (should use analytic_configurations.describe() instead)
            >>> sdk.analytic_configurations.search(filter={'_id': {'$eq': '506e0dcc965a0f56891f3860'}})
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]

            >>> # search configuration sets of a wanted analytic (can also use '$in')
            >>> sdk.analytic_configurations.search(filter={'analytic_name': {'$eq': 'my_analytic'}})
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]

            >>> # search configuration sets updated after December 15th 2021
            >>> sdk.analytic_configurations.search(filter={'modification_date': {'$gt': '2021-12-15T00:00:00'}})
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]

            >>> # get second page of the same search
            >>> sdk.analytic_configurations.search(filter={...}, page=1)
            [Resource(_id='61924899669e6e0007f8d261'), ...]

            >>> # search 400 first configuration sets sorted by name ascending, in 2 calls
            >>> sdk.analytic_configurations.search(sort={'name': 1}, limit=200)
            [Resource(_id='506e0dcc965a0f56891f3860'), ...]
            >>> sdk.analytic_configurations.search(sort={'name': 1}, limit=200, page=1)
            [Resource(_id='61924899669e6e0007f8d261'), ...]

            >>> # search configuration sets and also get the total results
            >>> sdk.analytic_configurations.search(filter={...}, return_total=True)
            ResourcesWithTotal(total=940, results=[Resource(_id='506e0dcc965a0f56891f3860'), ...])

        """

        return search(
            self,
            url='search-analytic-configurations',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, fields: dict = None,
                         limit: int = 100, page: int = None, sort: dict = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through analytic configuration sets.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found configuration sets are sorted chronologically by default in order to allow
        new resources to be found during the search.

        Args:
            filter: Optional ``filter`` dictionary from ``search()`` method.

            fields: Optional ``fields`` dictionary from ``search()`` method.

            limit: Optional maximum number of results by search
                request (default is ``100``).

            page: Optional page number to start the search at (default is 0).

            sort: Optional ``sort`` dictionary from ``search()`` method.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found analytic configuration sets.

        Examples:
            >>> # get all configurations matching filter by using generator
            >>> results_iterator = sdk.analytic_configurations.search_generator(filter={...})
            >>> configurations = [r for r in results_iterator]

        """
        return search_generator(self, first_page=0, filter=filter, fields=fields,
                                limit=limit, page=page, sort=sort, **kwargs)

    def update(self, configuration_set: ResourceId, *,
               name: str = None,
               description: str = None,
               versions: List[Dict[str, Any]] = None,
               value: Dict[str, Any] = None,
               analytic_version_range: str = None,
               **kwargs) -> Resource:
        """Update an analytic configuration set.

        At least one of ``name``, ``description```, ``versions``, or the
        couple ``value`` + ``analytic_version_range`` must be present.
        The couple ``value`` + ``analytic_version_range`` can be used if you had only
        one associated configuration, because it will erase all previous ones.
        If you have multiple configurations in your configuration set, you
        must use ``versions``.

        Args:
            configuration_set: Identifier of the configuration set to update.

            name: Optional new configuration set name.

            description: Optional new description.

            versions: Optional new associated configurations. It's a list of objects, each
                object must have both properties ``analytic_version_range`` and ``value``.
                It will replace all previous configurations in the configuration set.

            value: Optional new raw contents of the configuration, must be used with
                ``analytic_version_range`` (do not use with ``versions``). If this param
                is given, all previous configurations will be erased and replaced by one
                version containing this value and analytic_version_range.

            analytic_version_range: Optional version range of the analytic on which
                the first configuration can be applied, must be used with ``value``
                (do not use with ``versions``). Useless if ``value`` is not given.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Updated analytic configuration set resource.

        Examples:
            >>> # update configuration set's name
            >>> sdk.analytic_configurations.update('506e0dcc965a0f56891f3860', name='new name')
            Resource(_id='506e0dcc965a0f56891f3860')

            >>> # replace all configurations of the configuration set by a single new one
            >>> sdk.analytic_configurations.update('506e0dcc965a0f56891f3860',
            >>>     value={'...': '...'},
            >>>     analytic_version_range='1.x',
            >>> )
            Resource(_id='506e0dcc965a0f56891f3860')

            >>> # replace all configurations of the configuration set by multiple new ones
            >>> sdk.analytic_configurations.update('506e0dcc965a0f56891f3860',
            >>>     versions=[
            >>>         {'value': {'...': '...'}, 'analytic_version_range': '1.x' },
            >>>         {'value': {'...': '...'}, 'analytic_version_range': '1.7.x' },
            >>>         {'value': {'...': '...'}, 'analytic_version_range': '2.x' },
            >>>     ]
            >>> )
            Resource(_id='506e0dcc965a0f56891f3860')

        """

        data = kwargs

        for prop_name, val in [('analytic_configuration', configuration_set),
                               ('name', name),
                               ('description', description),
                               ('versions', versions)]:
            if val is not None:
                data.update({prop_name: val})

        if value is None and analytic_version_range is not None:
            raise QueryError('"analytic_version_range" is given but "value" is missing')

        if value is not None and analytic_version_range is None:
            raise QueryError('"value" is given but "analytic_version_range" is missing')

        if value is not None and analytic_version_range is not None:
            if 'versions' in data:
                raise QueryError('You cannot send both "versions" and couple '
                                 '"value"+"analytic_version_range"')
            data['versions'] = [{
                'analytic_version_range': analytic_version_range,
                'value': value,
            }]

        desc = self._provider.post(path='update-analytic-configuration', data=data)
        return Resource(**desc)

    def delete(self, configuration_set: SomeResourceIds, **kwargs) -> None:
        """Delete the specified analytic configuration set and the associated configuration(s).

        Args:
            configuration_set: Identifier of the configuration set to delete, or
                list of such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.
        """

        data = kwargs
        if isinstance(configuration_set, list):
            # the delete multiple is not available in the API, so do many simple delete
            for config_id in configuration_set:
                self.delete(config_id)

            # use these following lines when API will have the multiple delete:
            # ids_chunks = get_chunks(configuration, self._provider.max_per_delete)
            # for ids_chunk in ids_chunks:
            #     data['analytic_configurations'] = ids_chunk
            #     self._provider.post('delete-analytic-configurations', data=data)
        else:
            data['analytic_configuration'] = configuration_set
            self._provider.post('delete-analytic-configuration', data=data)

    def assign_to_company(self, configuration_set: ResourceId, *,
                          company: ResourceId,
                          **kwargs) -> dict:
        """Assign an analytic configuration set to a company.

        All analytic configurations that are currently part of this analytic configuration set
        (and the potential future ones) are assigned to the company.

        Args:
            configuration_set: Identifier of the configuration set to assign.

            company: Id of the company the analytic configuration set is assigned to.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Dict: A relation object containing Ids of Company, Analytic, and Configuration set.

        """

        data = kwargs

        data.update({
            'analytic_configuration': configuration_set,
            'company': company,
        })

        return self._provider.post(path='assign-analytic-configuration-to-company', data=data)

    def unassign_from_company(self, configuration_set: ResourceId, *,
                              company: ResourceId,
                              **kwargs):
        """Unassign an analytic configuration set from a company.

        Args:
            configuration_set: Identifier of the configuration set to assign.

            company: Id of the company the analytic configuration set is assigned to.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """

        data = kwargs

        data.update({
            'analytic_configuration': configuration_set,
            'company': company,
        })

        self._provider.post(path='unassign-analytic-configuration-from-company',
                            data=data, as_json=False)
