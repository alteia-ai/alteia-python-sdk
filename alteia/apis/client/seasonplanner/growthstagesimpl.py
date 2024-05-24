from typing import List, Union

from alteia.apis.provider import SeasonPlannerAssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class GrowthStagesImpl:
    def __init__(self, season_planner_asset_management_api: SeasonPlannerAssetManagementAPI,
                 **kwargs):
        self._provider = season_planner_asset_management_api

    def create(self, *, company: ResourceId, name: str, **kwargs) -> Resource:
        """Create a growth-stage.

        Args:
            company: Identifier of the company.

            name: growth-stage name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A growth-stage resource.
        """
        data = kwargs
        data.update({
            'company': company,
            'name': name
        })

        content = self._provider.post(path='create-growth-stage', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search growth-stages.

        Args:
            filter: Search filter dictionary.
                    {
                        "_id": {
                            "$eq": "string"
                        },
                        "company": {
                            "$eq": "string"
                        },
                        "creation_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "modification_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "deletion_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "name": {
                            "$eq": "string"
                        },
                    }

            limit: Maximum number of results to extract. Default: 1000.

            page: Page number (starting at page 0).

            fields: Optional properties to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Resources: A list of resources OR a namedtuple
                with total number of results and list of resources.

        """
        return search(
            self,
            url='search-growth-stages',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, growth_stage: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a growth-stage or a list of growth-stages.

        Args:
            growth_stage: Identifier of the growth-stage to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The growth-stage description or a list of growth-stages descriptions.

        """
        data = kwargs
        if isinstance(growth_stage, list):
            results = []
            ids_chunks = get_chunks(growth_stage, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['growth_stages'] = ids_chunk
                descs = self._provider.post('describe-growth-stages', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['growth_stage'] = growth_stage
            desc = self._provider.post('describe-growth-stage', data=data)
            return Resource(**desc)

    def update(self, *, growth_stage: ResourceId, name: str,
               company: str = None, **kwargs) -> Resource:
        """Update a growth-stage.

        Args:
            growth_stage: Identifier of the growth-stage.

            name: growth-stage name.

            company: Optional identifier of the company.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A growth-stage resource updated.
        """
        data = kwargs
        data.update({
            'growth_stage': growth_stage,
            'name': name
        })

        if company is not None:
            data['company'] = company

        content = self._provider.post(path='update-growth-stage', data=data)

        return Resource(**content)

    def delete(self, growth_stage: ResourceId, **kwargs):
        """Delete a growth-stage.

        Args:
            growth_stage: Identifier of the growth-stage to delete.

        """

        data = kwargs
        data['growth_stage'] = growth_stage

        self._provider.post('delete-growth-stage', data=data)
