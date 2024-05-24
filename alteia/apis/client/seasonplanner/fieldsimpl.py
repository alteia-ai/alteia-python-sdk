from typing import List, Union

from alteia.apis.provider import SeasonPlannerAssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class FieldsImpl:
    def __init__(self, season_planner_asset_management_api: SeasonPlannerAssetManagementAPI,
                 **kwargs):
        self._provider = season_planner_asset_management_api

    def create(self, *, company: ResourceId, project: ResourceId, name: str,
               description: str = None, **kwargs) -> Resource:
        """Create a field.

        Args:
            company: Identifier of the company.

            project: Identifier of the project.

            name: Field name.

            description: Optional description.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A field resource.
        """
        data = kwargs
        data.update({
            'company': company,
            'project': project,
            'name': name
        })

        if description is not None:
            data['description'] = description

        content = self._provider.post(path='create-field', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search fields.

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
            url='search-fields',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, field: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a field or a list of fields.

        Args:
            field: Identifier of the field to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The field description or a list of fields descriptions.

        """
        data = kwargs
        if isinstance(field, list):
            results = []
            ids_chunks = get_chunks(field, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['fields'] = ids_chunk
                descs = self._provider.post('describe-fields', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['field'] = field
            desc = self._provider.post('describe-field', data=data)
            return Resource(**desc)

    def update(self, *, field: ResourceId, project: ResourceId, name: str,
               company: str = None, description: str = None, **kwargs) -> Resource:
        """Update a field.

        Args:
            field: Identifier of the field.

            project: Identifier of the project.

            name: Field name.

            company: Optional identifier of the company.

            description: Optional description.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A field resource updated.
        """
        data = kwargs
        data.update({
            'field': field,
            'project': project,
            'name': name
        })

        for param_name, param_value in (('company', company),
                                        ('description', description)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-field', data=data)

        return Resource(**content)

    def delete(self, field: ResourceId, **kwargs):
        """Delete a field.

        Args:
            field: Identifier of the field to delete.

        """

        data = kwargs
        data['field'] = field

        self._provider.post('delete-field', data=data)
