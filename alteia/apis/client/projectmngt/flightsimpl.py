from typing import List

from alteia.apis.provider import ProjectManagerAPI
from alteia.core.errors import ResponseError
from alteia.core.resources.projectmngt.flights import Flight
from alteia.core.utils.typing import ResourceId


class FlightsImpl:
    def __init__(self, project_manager_api: ProjectManagerAPI, **kwargs):
        self._provider = project_manager_api

    def create(self, *args, **kwargs):
        raise NotImplementedError('missions.create() must be used instead')

    def describe(self, flight: ResourceId) -> Flight:
        """Describe the flight with the given identifier.

        Args:
            flight: The flight identifier.

        Returns:
            Resource: The flight resource with identifier equal to ``id``.

        """
        query = {
            "flights_id": [flight]
        }
        content = self._provider.search(path='flights', query=query)
        flights = content.get('flights', [])
        if len(flights) != 1:
            raise ResponseError('Flight not found')
        return Flight(**flights[0])

    def search(self, *, project: ResourceId = None,
               mission: ResourceId = None) -> List[Flight]:
        """Search flights attached to the project mission.

        Args:
            project: The project identifier where flights are searched.

            mission: The mission identifier where flights are searched.

        Returns:
             [Resource]: List of flights found.

        """
        query = {}
        if project is not None:
            query.update({'project_id': project})
        elif mission is not None:
            query.update({'mission_id': mission})

        content = self._provider.search(path='flights', query=query)

        return [Flight(**d) for d in content.get('flights')]
