"""Implementation of missions.

"""
from typing import List, Optional

from alteia.apis.provider import ProjectManagerAPI, UIServicesAPI
from alteia.core.errors import QueryError
from alteia.core.resources.projectmngt.flights import Flight
from alteia.core.resources.projectmngt.missions import Mission
from alteia.core.utils.typing import ResourceId


class MissionsImpl:
    def __init__(self, project_manager_api: ProjectManagerAPI,
                 ui_services_api: UIServicesAPI, **kwargs):
        self._provider = project_manager_api
        self._alt_provider = ui_services_api

    def create(self, *, project: ResourceId, survey_date: str,
               number_of_images: int, name: str = None, **kwargs
               ) -> (Flight, Mission):
        """Creates a mission.

        Based on the number of images to attach to the mission,
        this function calls ``create_survey()`` or ``create_mission()``.

        Args:
            project: Identifier of the project on which the mission is added.

            survey_date: Survey date of the mission
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            number_of_images: Number of images that will be uploaded.

            name: Optional mission name.

            **kwargs: Optional arguments that will be merged into the
              mission description.

        Returns:
            (Flight, Mission): A tuple with the created flight and mission.
            ``Flight = None`` when the number of images is 0.

        """
        if name:
            kwargs.update({'name': name})

        if number_of_images > 0:
            flight, mission = self.create_survey(
                survey_date=survey_date,
                project=project,
                number_of_images=number_of_images,
                **kwargs
            )
        else:
            mission = self.create_mission(
                project=project,
                survey_date=survey_date,
                **kwargs
            )
            flight = None
        return flight, mission

    def create_mission(self, *, project: ResourceId, survey_date: str,
                       name: str = None, **kwargs) -> Mission:
        """Creates a mission without images.

        This function is used when no image is attached to the mission.
        As a consequence, no flight will be created.

        Args:
            project: Identifier of the project on which the mission is added.

            survey_date: Survey date of the mission
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            name: Optional mission name.

            **kwargs: Optional arguments that will be merged into the
              mission description.

        Returns:
            Mission: The created mission.

        """

        params_mission = {
            'project': project,
            'survey_date': survey_date}

        if name:
            params_mission.update({'name': name})

        params_mission.update(kwargs)

        content = self._alt_provider.post(
            path='missions', data=params_mission)

        mission_desc = content.get('mission')

        return Mission(**mission_desc)

    def create_survey(self, *,
                      survey_date: str,
                      project: ResourceId,
                      number_of_images: int,
                      name: str = None,
                      coordinates: List = None,
                      area: float = 0,
                      **kwargs) -> (Flight, Mission):
        """Create a survey (mission + flight).

        This function is used when images will be attached to the mission.
        As a consequence, a flight will be created as well.

        Args:
            survey_date: Survey date (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            project: Project identifier on which the survey is added.

            number_of_images: Number of photos that will be uploaded.

            name: Optional mission name.

            coordinates: Coordinates bounding the mission to create.

            area: Optional survey area.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            QueryError: The survey creation response is incorrect.

        Returns:
            (Flight, Mission): A tuple with the created flight and mission.

        """

        params_survey = {
            'project_id': project,
            'survey_date': survey_date,
            'number_of_photos': number_of_images,
            'orderAnalytic': {},
            'processSettings': {},
            'addProjectToUsers': True,
            'area': area
        }

        if name:
            params_survey.update({'name': name, 'mission_name': name})
        else:
            # 'name' is required for the flight name (but never displayed)
            params_survey.update({'name': ''})

        if coordinates is not None:
            params_survey['geometry'] = {
                'type': 'GeometryCollection',
                'geometries': [
                    {
                        'type': 'Polygon',
                        'coordinates': [coordinates]
                    }
                ]}

        params_survey.update(kwargs)

        content = self._alt_provider.post(
            path='projects/survey', data=params_survey)

        mission_desc = content.get('mission')
        flight_desc = content.get('flight')

        if mission_desc is None:
            raise QueryError('"mission" is missing in the response content')
        if flight_desc is None:
            raise QueryError('"flight" is missing in the response content')

        mission = Mission(**mission_desc)
        flight = Flight(**flight_desc)

        return flight, mission

    def delete(self, mission: ResourceId):
        """Delete a mission.

        Args:
            mission: Identifier of the mission to delete.

        """
        self._alt_provider.post(
            path='missions/delete-survey', data={'mission': mission})

    def search(self, *, missions: List[ResourceId] = None,
               flights: List[ResourceId] = None,
               project: ResourceId = None,
               deleted: bool = False,
               **kwargs) -> List[Mission]:
        """Search missions.

        Args:
            missions: Optional list of mission identifiers.

            flights: Optional list of flight identifiers.

            project: Optional project identifier.

            deleted: Optional parameter to search for deleted missions or not
                (``False`` by default).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            QueryError: When the response is not consistent.

        Returns:
             [Mission]: List of missions matching the search criteria.

        Examples:
            Get the missions related to a specific project:

            >>> sdk.missions.search(project=my_project_resource.id)
            [<alteia.core.resources.projectmngt.missions.Mission...>, ...]
        """
        data = kwargs

        if missions:
            data.update({'_id': missions})

        for param_name, param_value in (('project', project),
                                        ('flights', flights),
                                        ('deleted', deleted)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._alt_provider.post(path='missions/search', data=data)

        if 'missions' not in content:
            raise QueryError('"missions" item should be in the response content')

        return [Mission(**d) for d in content['missions']]

    def complete_survey_upload(self, *, flight: ResourceId,
                               status: str = 'complete'):
        """Complete the survey upload.

        It notifies the front-end that all the images have been uploaded.
        It is necessary after the ``create_survey``. Otherwise, the upload
        progression bar will still be displayed.


        Args:
            flight: Flight identifier.

            status: Upload completion status (``complete`` or ``'failed``).

        Raises:
            QueryError: When the response is not consistent.

        """

        data = {"_id": flight, "status": status}

        path = "flights/{}/uploads/status".format(flight)
        content = self._provider.post(path=path, data=data, as_json=False)

        if content != b'OK':
            raise QueryError(
                'Complete survey response is not "OK" as expected; '
                '"{}" received'.format(content[0:100]))

    def describe(self, mission: ResourceId,
                 deleted: bool = False) -> Optional[Mission]:
        """Describe the mission for the specified id.

        Args:
            mission: Mission identifier.

            deleted: Optional parameter to describe a deleted mission or not
                (``False`` by default).

        Returns:
            Mission: Mission resource matching the id (``None`` if not found).

        Examples:
            >>> sdk.missions.describe('5ce7f379327e9d5f15e37bb5')
            <alteia.core.resources.projectmngt.missions.Mission...>

        """
        found = self.search(missions=[mission], deleted=deleted)
        if len(found) < 1:
            return None
        else:
            return found[0]

    def rename(self, mission: ResourceId, *, name: str, **kwargs
               ) -> Optional[Mission]:
        """Rename the given mission.

        Args:
            mission: Mission identifier.

            name: Name to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        data['mission'] = mission
        data['name'] = name

        content = self._alt_provider.post(path='missions/rename-survey', data=data)
        return Mission(**content)
