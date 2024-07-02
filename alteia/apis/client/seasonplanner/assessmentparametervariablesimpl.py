from typing import List, Union

from alteia.apis.provider import SeasonPlannerAssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class AssessmentParameterVariablesImpl:
    def __init__(self, season_planner_asset_management_api: SeasonPlannerAssetManagementAPI,
                 **kwargs):
        self._provider = season_planner_asset_management_api

    def create(self, *, company: ResourceId, name: str, **kwargs) -> Resource:
        """Create a assessment-parameter-variable.

        Args:
            company: Identifier of the company.

            name: assessment-parameter-variable name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: An assessment-parameter-variable resource.
        """
        data = kwargs
        data.update({
            'company': company,
            'name': name
        })

        content = self._provider.post(
            path='create-assessment-parameter-variable',
            data=data
        )

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search assessment-parameter-variable.

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

        Returns:
            Resources: A list of resources OR a namedtuple
                with total number of results and list of resources.

        """
        return search(
            self,
            url='search-assessment-parameter-variables',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, assessment_parameter_variable: SomeResourceIds,
                 **kwargs) -> SomeResources:
        """Describe a assessment-parameter-variable
            or a list of assessment-parameter-variables.

        Args:
            assessment_parameter_variable: Identifier of the
                assessment-parameter-variable to describe,
                or list of such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The assessment-parameter-variable description
                or a list of assessment-parameter-variables descriptions.

        """
        data = kwargs
        if isinstance(assessment_parameter_variable, list):
            results = []
            ids_chunks = get_chunks(
                assessment_parameter_variable,
                self._provider.max_per_describe
            )
            for ids_chunk in ids_chunks:
                data['assessment_parameter_variables'] = ids_chunk
                descs = self._provider.post(
                    'describe-assessment-parameter-variables',
                    data=data
                )
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['assessment_parameter_variable'] = assessment_parameter_variable
            desc = self._provider.post(
                'describe-assessment-parameter-variable',
                data=data
            )
            return Resource(**desc)

    def update(self, *, assessment_parameter_variable: ResourceId, name: str,
               company: str = None, custom_ids: str = None, **kwargs) -> Resource:
        """Update a assessment-parameter-variable.

        Args:
            assessment_parameter_variable: Identifier of the assessment-parameter-variable.

            name: assessment-parameter-variable name.

            company: Optional identifier of the company.

            custom_ids: Optional custom ids.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A assessment-parameter-variable resource updated.
        """
        data = kwargs
        data.update({
            'assessment_parameter_variable': assessment_parameter_variable,
            'name': name
        })

        for param_name, param_value in (('company', company),
                                        ('custom_ids', custom_ids)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(
            path='update-assessment-parameter-variable',
            data=data
        )

        return Resource(**content)

    def delete(self, assessment_parameter_variable: ResourceId, **kwargs):
        """Delete a assessment-parameter-variable.

        Args:
            assessment_parameter_variable: Identifier of the
                assessment-parameter-variable to delete.

        """

        data = kwargs
        data['assessment_parameter_variable'] = assessment_parameter_variable

        self._provider.post('delete-assessment-parameter-variable', data=data)
