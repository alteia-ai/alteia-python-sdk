from typing import List, Union

from alteia.apis.provider import SeasonPlannerAssetManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class EstimationMethodsImpl:
    def __init__(self, season_planner_asset_management_api: SeasonPlannerAssetManagementAPI,
                 **kwargs):
        self._provider = season_planner_asset_management_api

    def create(self, *, name: str, companies: ResourceId, input_data_requirements: dict,
               crops: list, description: str = None, status: str = None, analytic: dict = None,
               growth_stages: list = None, **kwargs) -> Resource:
        """Create an estimation-method.

        Args:
            name: Name of the estimation method.

            companies: List of companies identifiers.

            input_data_requirements: Estimation method data collection requirements.
                                     input_data_requirements:{
                                        "sensor_type": "hs",
                                        "carrier_type": "fixed-wing",
                                        "bands":
                                            [{
                                                "name": "string",
                                                "full_width_half_maximum": 0,
                                                "central_wavelength": 0
                                            }],
                                        "gsd": {
                                            "value": 0,
                                            "unit": "m"
                                        },
                                        "overlap": {
                                            "forward": 100,
                                            "lateral": 100
                                        },
                                        "speed": {
                                            "value": 0,
                                            "unit": "m/s"
                                        },
                                        "ppk_rtk": {
                                            "use": true
                                        },
                                        "calibration": {
                                            "use": true
                                        },
                                        "gcp": {
                                            "type": "none"
                                        }}

            crops: List of associated crops identifiers.

            description: Optional description of the estimation method.

            status: Optional status of the estimation method, ``development`` ``validated``.

            analytic: Optional estimation method analytic definition.
                      That defines assessment parameters computation.
                      analytic: {
                        "name": "plant_height_for_trial_field",
                        "inputs_mapping": {
                            "analytic_input_name": "collection_task_deliverable_name",
                            "dsm_in": "dsm"
                        },
                        "parameters": {},
                        "outputs_mapping": {
                            "analytic_deliverable_name": {
                                "assessment_parameter_id1": "deliverable_prop_name_x",
                                "assessment_parameter_id2": "deliverable_prop_name_y"
                            },
                            plant_height_estimation": {
                                "assessment_parameter_id3": "deliverable_prop_name_z"
                            }
                        },
                        "version_range": [
                            "1 (means >=1.0.0 and < 2.0.0)",
                            "1.x (same)",
                            "1.0.0 (strict contraint)",
                            "1.0.x (means >=1.0.0 and <1.1.0)"
                        ]
                      }

            growth_stages: Optional list of associated growth stages identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A estimation-method resource.
        """
        data = kwargs
        data.update({
            'name': name,
            'companies': companies,
            'input_data_requirements': input_data_requirements,
            'crops': crops
        })

        for param_name, param_value in (('description', description),
                                        ('status', status),
                                        ('analytic', analytic),
                                        ('growth_stages', growth_stages)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-estimation-method', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search estimation-methods.

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
            url='search-estimation-methods',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, estimation_method: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe an estimation-methods or a list of estimation-methodss.

        Args:
            estimation_method: Identifier of the estimation-methods to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The estimation-methods description or
                      a list of estimation-methodss descriptions.

        """
        data = kwargs
        if isinstance(estimation_method, list):
            results = []
            ids_chunks = get_chunks(estimation_method, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['estimation_methods'] = ids_chunk
                descs = self._provider.post('describe-estimation-methods', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['estimation_method'] = estimation_method
            desc = self._provider.post('describe-estimation-method', data=data)
            return Resource(**desc)

    def update(self, *, estimation_method: ResourceId, crops: list,
               name: str = None, description: str = None, status: str = None,
               companies: list = None, input_data_requirements: dict = None,
               analytic: dict = None, growth_stages: dict = None, **kwargs) -> Resource:
        """Update an estimation-method.

        Args:
            estimation_method: Identifier of the estimation-method.

            crops: List of associated crops identifiers.

            name: Optional name of the estimation method.

            description: Optional description of the estimation method.

            status: Optional status of the estimation method, ``development`` ``validated``.

            companies: Optional ist of companies identifiers.

            input_data_requirements: Optional estimation method data collection requirements.
                                     input_data_requirements:{
                                        "sensor_type": "hs",
                                        "carrier_type": "fixed-wing",
                                        "bands":
                                            [{
                                                "name": "string",
                                                "full_width_half_maximum": 0,
                                                "central_wavelength": 0
                                            }],
                                        "gsd": {
                                            "value": 0,
                                            "unit": "m"
                                        },
                                        "overlap": {
                                            "forward": 100,
                                            "lateral": 100
                                        },
                                        "speed": {
                                            "value": 0,
                                            "unit": "m/s"
                                        },
                                        "ppk_rtk": {
                                            "use": true
                                        },
                                        "calibration": {
                                            "use": true
                                        },
                                        "gcp": {
                                            "type": "none"
                                        }}

            analytic: Optional estimation method analytic definition.
                      That defines assessment parameters computation.
                      analytic: {
                        "name": "plant_height_for_trial_field",
                        "inputs_mapping": {
                            "analytic_input_name": "collection_task_deliverable_name",
                            "dsm_in": "dsm"
                        },
                        "parameters": {},
                        "outputs_mapping": {
                            "analytic_deliverable_name": {
                                "assessment_parameter_id1": "deliverable_prop_name_x",
                                "assessment_parameter_id2": "deliverable_prop_name_y"
                            },
                            plant_height_estimation": {
                                "assessment_parameter_id3": "deliverable_prop_name_z"
                            }
                        },
                        "version_range": [
                            "1 (means >=1.0.0 and < 2.0.0)",
                            "1.x (same)",
                            "1.0.0 (strict contraint)",
                            "1.0.x (means >=1.0.0 and <1.1.0)"
                        ]
                      }

            growth_stages: Optional list of associated growth stages identifiers.

        Returns:
            Resource: A estimation-method resource updated.
        """
        data = kwargs
        data.update({
            'estimation_method': estimation_method,
            'crops': crops
        })

        for param_name, param_value in (('name', name),
                                        ('description', description),
                                        ('status', status),
                                        ('companies', companies),
                                        ('input_data_requirements', input_data_requirements),
                                        ('analytic', analytic),
                                        ('growth_stages', growth_stages)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-estimation-method', data=data)

        return Resource(**content)

    def delete(self, estimation_method: ResourceId, **kwargs):
        """Delete an estimation-method.

        Args:
            estimation_method: Identifier of the estimation-method to delete.

        """

        data = kwargs
        data['estimation_method'] = estimation_method

        self._provider.post('delete-estimation-method', data=data)

    def list_deliverables_definitions(self, *, sensor_type: str, task_purpose: str = "mapping",
                                      **kwargs) -> List[dict]:
        """List of the available deliverable definitions for an estimation method.

        Args:
            sensor_type: Sensor type: ``hs``, ``lidar``,``ms``,``rgb``.

            task_purpose: Default ``mapping``, enum: ``3d-modeling``, ``raw``

        Returns:
            List of deliverables

        """

        data = kwargs
        data['sensor_type'] = sensor_type

        for param_name, param_value in (('task_purpose', task_purpose),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='list-deliverable-definitions', data=data)

        return [c for c in content]
