from typing import List

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources


class CarrierModelsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, name: str, maker: str, type: str, company: ResourceId = None,
               unloaded_weight: dict = None, flight_time: dict = None,
               speed: dict = None, altitude: dict = None,
               compatible_sensor_models: List[ResourceId] = None, **kwargs) -> Resource:
        """Create a carrier model.

        Args:
            name: Carrier model name.

            maker: Maker name.

            type: Model type, among``fixed-wind``, ``multirotor``, ``ground-robot``,
            ``helicopter``, ``pedestrian``.

            company: Optional identifier of the company.

            unloaded_weight: Optional unloaded weight
                ``{ value: weight without sensor, unit: unit (g, kg) }``.

            flight_time : Optional flight time
                ``{ value: maximum flight time, unit: unit (min) }``.

            speed : Optional speed
                ``{ min: {value, unit}, max: {value, unit(m/s, mph ,ft/s, km/h, knot)} }``.

            altitude : Optional altitude ``{ min: {value, unit}, max: {value, unit(m, ft)} }``.

            compatible_sensor_models: Optional list of compatible sensors identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A carrier model resource.
        """
        data = kwargs
        data.update({
            'name': name,
            'maker': maker,
            'type': type
        })

        for param_name, param_value in (('company', company),
                                        ('unloaded_weight', unloaded_weight),
                                        ('flight_time', flight_time),
                                        ('speed', speed),
                                        ('altitude', altitude),
                                        ('unloaded_weight', unloaded_weight),
                                        ('compatible_sensor_models', compatible_sensor_models)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-carrier-model', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, **kwargs
               ) -> List[Resource]:
        """Search carrier models.

        Args:
            filter: Search filter dictionary.

            limit: Maximum number of results to extract.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resources: A list of carrier models resources.

        """

        data = kwargs

        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post('search-carrier-models', data=data)
        results = r.get('results')

        return [Resource(**m) for m in results]

    def describe(self, carrier_models: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a carrier model or a list of carrier models.

        Args:
            carrier_models: Identifier of the carrier model to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The carrier model description
                or a list of carrier model descriptions.

        """
        data = kwargs
        if isinstance(carrier_models, list):
            data['carrier_models'] = carrier_models
            descs = self._provider.post('describe-carrier-models', data=data)
            return [Resource(**desc) for desc in descs]
        else:
            data['carrier_model'] = carrier_models
            desc = self._provider.post('describe-carrier-model', data=data)
            return Resource(**desc)

    def delete(self, carrier_model: ResourceId, **kwargs):
        """Delete a carrier model.

        Args:
            carrier_model: Carrier model to delete.

        """

        data = kwargs
        data['carrier_model'] = carrier_model

        self._provider.post('delete-carrier-model', data=data)
