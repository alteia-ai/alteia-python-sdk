from typing import List, Union

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class SensorsModelsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, name: str, maker: str, type: str, company: ResourceId = None,
               weight: dict = None, lens_type: str = None, width: str = None, height: str = None,
               focal_length: float = None, pixel_size: float = None, principal_point: list = None,
               distortion: dict = None, bands: list = None, **kwargs) -> Resource:
        """Create a sensor model.

        Args:
            name: sensor model name.

            maker: Maker name.

            type: Model type, ``rgb``, ``ms``, ``hs``,
            ``lidqar``, ``thermal``.

            company: Optional identifier of the company.

            weight: Optional unloaded weight.
                ``{ value: weight, unit: unit (g, kg) }``.

            lens_type : Optional sensor lens type, ``perspective`` or ``fisheye``.

            width : Optional sensor width.

            height : Optional sensor height.

            focal_length: Optional sensor focal length.

            pixel_size: Optional sensor pixel size.

            principal_point: Optional sensor principal point.

            distortion: Optional sensor distortion.

            bands: Optional sensor bands.
                   ``[
                    {
                        "name": "string",
                        "full_width_half_maximum": 0,
                        "central_wavelength": 0
                        }
                    ]``

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A sensor model resource.
        """
        data = kwargs
        data.update({
            'name': name,
            'maker': maker,
            'type': type
        })

        for param_name, param_value in (('company', company),
                                        ('weight', weight),
                                        ('lens_type', lens_type),
                                        ('width', width),
                                        ('height', height),
                                        ('focal_length', focal_length),
                                        ('pixel_size', pixel_size),
                                        ('principal_point', principal_point),
                                        ('distortion', distortion),
                                        ('bands', bands)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-sensor-model', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search sensor models.

        Args:
            filter: Search filter (refer to
                ``/search-sensor-model`` definition in data capture
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
            url='search-sensor-models',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, sensor_models: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a sensor model or a list of sensor models.

        Args:
            sensor_models: Identifier of the sensor model to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The sensor model description
                or a list of sensor model descriptions.

        """
        data = kwargs
        if isinstance(sensor_models, list):
            results = []
            ids_chunks = get_chunks(sensor_models, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['sensor_models'] = ids_chunk
                descs = self._provider.post('describe-sensor-models', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['sensor_model'] = sensor_models
            desc = self._provider.post('describe-sensor-model', data=data)
            return Resource(**desc)

    def delete(self, sensor_model: ResourceId, **kwargs):
        """Delete a sensor model.

        Args:
            sensor_model: sensor model to delete.

        """

        data = kwargs
        data['sensor_model'] = sensor_model

        self._provider.post('delete-sensor-model', data=data)
