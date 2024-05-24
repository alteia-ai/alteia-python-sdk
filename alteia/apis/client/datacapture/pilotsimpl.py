from typing import List, Union

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class PilotsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, user: ResourceId, teams: List[ResourceId],
               carrier_models: List[ResourceId] = None, sensor_models: List[ResourceId] = None,
               **kwargs) -> Resource:
        """Create a pilot.

        Args:
            user: Identifier of the user.

            teams: List of identifiers of the team.

            carrier_models: Optional List of identifiers of carrier models.

            sensor_models : Optional List of identifiers of sensor models.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A pilot resource.
        """
        data = kwargs
        data.update({
            'user': user,
            'teams': teams
        })

        for param_name, param_value in (('carrier_models', carrier_models),
                                        ('sensor_models', sensor_models)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-pilot', data=data)

        return Resource(**content)

    def describe(self, pilot: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a pilot or list of pilots.

                Args:
                    pilot: Identifier of the pilot to describe, or list of
                        such identifiers.

                    **kwargs: Optional keyword arguments. Those arguments are
                        passed as is to the API provider.

                Returns:
                    Resource: A pilot resource or a list of pilot resources.

                """
        data = kwargs
        if isinstance(pilot, list):
            results = []
            ids_chunks = get_chunks(pilot, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['pilots'] = ids_chunk
                descs = self._provider.post('describe-pilots', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['pilot'] = pilot
            desc = self._provider.post('describe-pilot', data=data)
            return Resource(**desc)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search pilots.

        Args:
            filter: Search filter (refer to
                ``/search-pilots`` definition in data capture
                management API for a detailed description
                of supported operators).

            limit: Optional Maximum number of results to extract.

            fields: Optional properties to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            page: Optional Page number (starting at page 0).

            sort: Optional. Sort the results on the specified attributes
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
            url='search-pilots',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def update(self, *, pilot: ResourceId, teams: List[ResourceId] = None,
               carrier_models: List[ResourceId] = None, sensor_models: List[ResourceId] = None,
               **kwargs) -> Resource:
        """Update a pilot.

        Args:
            pilot: Identifier of the pilot.

            teams: List of identifiers of the team.

            carrier_models: Optional List of identifiers of carrier models.

            sensor_models : Optional List of identifiers of sensor models.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A pilot updated.
        """
        data = kwargs
        data['pilot'] = pilot

        for param_name, param_value in (('teams', teams),
                                        ('carrier_models', carrier_models),
                                        ('sensor_models', sensor_models)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-pilot', data=data)

        return Resource(**content)

    def delete(self, pilot: ResourceId, **kwargs):
        """Delete a pilot.

        Args:
            sensor: Identifier of the pilot to delete.

        """

        data = kwargs
        data['pilot'] = pilot

        self._provider.post('delete-pilot', data=data)
