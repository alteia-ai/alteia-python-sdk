from typing import List, Union

from alteia.apis.provider import SeasonPlannerTrialManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class SeasonPlannerMissionsImpl:
    def __init__(self, season_planner_trial_management_api: SeasonPlannerTrialManagementAPI,
                 **kwargs):
        self._provider = season_planner_trial_management_api

    def add_mission_to_trial(self, *, trial: ResourceId, name: str, start_date: str = None,
                             end_date: str = None, description: str = None,
                             estimation_methods: list = None, growth_stages_range: dict = None,
                             **kwargs) -> Resource:
        """Create a new mission on the specified trial.

        The created mission will have the company of the trial.

        Args:
            trial: Trial identifier.

            name: name of the mission.

            start_date: Optional start date range ``2019-08-24T14:15:22Z``.

            end_date: Optional end date range ``2019-08-24T14:15:22Z``.

            description: Optional description of the mission.

            estimation_methods: Optional estimation methods linked to the mission.

            growth_stages_range: Optional growth stages associated to a mission.
                                {
                                    "from": "5f031dd9a6f7f53d73962efb",
                                    "to": "5f031dd9a6f7f53d73962efb"
                                }

        Returns:
            Resource: A trial resource.
        """
        data = kwargs
        data['trial'] = trial
        data['name'] = name

        for param_name, param_value in (('start_date', start_date),
                                        ('end_date', end_date),
                                        ('description', description),
                                        ('estimation_methods', estimation_methods),
                                        ('growth_stages_range', growth_stages_range),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='add-mission-to-trial', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search missions.

        Args:
            filter: Search filter dictionary.
                    ``"_id": {
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
                        "trial": {
                            "$eq": "string"
                        },
                    }``

            limit: Optional Maximum number of results to extract. Default: 5000.

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
            Resources: A list of mission resources.

        """

        return search(
            self,
            url='search-missions',
            filter=filter,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def describe(self, mission: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a mission.

        Args:
            mission: Identifier of the mission to describe, or list of
                such identifiers.

        Returns:
            Resource: The mission description
                or a list of mission descriptions.

        """
        data = kwargs
        if isinstance(mission, list):
            results = []
            ids_chunks = get_chunks(mission, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['missions'] = ids_chunk
                descs = self._provider.post('describe-missions', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['mission'] = mission
            desc = self._provider.post('describe-mission', data=data)
            return Resource(**desc)

    def update_mission(self, *, mission: ResourceId, name: str, start_date: str = None,
                       end_date: str = None, description: str = None,
                       estimation_methods: list = None, growth_stages_range: dict = None,
                       **kwargs) -> Resource:
        """Update a mission.

        Args:
            mission: Mission identifier.

            name: name of the mission.

            start_date: Optional start date range ``2019-08-24T14:15:22Z``.

            end_date: Optional end date range ``2019-08-24T14:15:22Z``.

            description: Optional description of the mission.

            estimation_methods: Optional estimation methods linked to the mission.

            growth_stages_range: Optional growth stages associated to a mission.
                                {
                                    "from": "5f031dd9a6f7f53d73962efb",
                                    "to": "5f031dd9a6f7f53d73962efb"
                                }

        Returns:
            Resource: A mission resource.
        """
        data = kwargs
        data['mission'] = mission
        data['name'] = name

        for param_name, param_value in (('start_date', start_date),
                                        ('end_date', end_date),
                                        ('description', description),
                                        ('estimation_methods', estimation_methods),
                                        ('growth_stages_range', growth_stages_range),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-mission', data=data)

        return Resource(**content)

    def delete(self, mission: ResourceId, **kwargs):
        """Delete a mission.

        Args:
            mission: Identifier of the mission to delete.

        """

        data = kwargs
        data['mission'] = mission

        self._provider.post('delete-mission', data=data)
