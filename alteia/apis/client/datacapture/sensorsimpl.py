from typing import List, Union

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class SensorsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, sensor_model: str, team: ResourceId, serial_number: str,
               firmware: str = None, comment: str = None, **kwargs) -> Resource:
        """Create a sensor.

        Args:
            sensor_model: Identifier of the sensor model.

            team: Identifier of the team.

            serial_number: Serial number of the sensor.

            firmware : Optional firmware.

            comment: Optional comment.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A sensor resource.
        """
        data = kwargs
        data.update({
            'sensor_model': sensor_model,
            'team': team,
            'serial_number': serial_number
        })

        for param_name, param_value in (('comment', comment),
                                        ('firmware', firmware)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-sensor', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search sensors.

        Args:
            filter: Search filter (refer to
                ``/search-sensors`` definition in data capture
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
            url='search-sensors',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, sensor: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a sensor or a list of sensors.

        Args:
            sensor: Identifier of the sensor to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The sensor description or a list of sensors descriptions.

        """
        data = kwargs
        if isinstance(sensor, list):
            results = []
            ids_chunks = get_chunks(sensor, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['sensors'] = ids_chunk
                descs = self._provider.post('describe-sensors', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['sensor'] = sensor
            desc = self._provider.post('describe-sensor', data=data)
            return Resource(**desc)

    def delete(self, sensor: ResourceId, **kwargs):
        """Delete a sensor.

        Args:
            sensor: Identifier of the sensor to delete.

        """

        data = kwargs
        data['sensor'] = sensor

        self._provider.post('delete-sensor', data=data)
