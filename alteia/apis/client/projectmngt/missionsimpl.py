"""Implementation of missions.

"""
from typing import Dict, Generator, List, Optional, Tuple, Union

from alteia.apis.provider import ProjectManagerAPI
from alteia.core.errors import QueryError
from alteia.core.resources.projectmngt.flights import Flight
from alteia.core.resources.projectmngt.missions import Mission
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class MissionsImpl:

    def __init__(self, project_manager_api: ProjectManagerAPI, **kwargs):
        self._provider = project_manager_api

    def create(
        self,
        *,
        project: ResourceId,
        survey_date: str,
        number_of_images: int,
        name: str = None,
        **kwargs
    ) -> Tuple[Optional[Flight], Mission]:
        """Creates a mission.

        Based on the number of images to attach to the mission,
        this function calls ``create_survey()`` or ``create_mission()``.
        If you have images, you also have to send ``coordinates`` or
        ``geometry`` (not both).

        Args:
            project: Identifier of the project on which the mission is added.

            survey_date: Survey date of the mission
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            number_of_images: Number of images that will be uploaded.

            name: Optional mission name.

            **kwargs: Optional arguments that will be merged into the
                mission description.

        Returns:
            Tuple[Flight, Mission]: A tuple with the created flight and mission.
                ``Flight = None`` when the number of images is 0.

        """
        flight: Optional[Flight]

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

        content = self._provider.post(
            path='missions', data=params_mission)

        mission_desc = content.get('mission')

        return Mission(**mission_desc)

    def create_survey(self, *,
                      survey_date: str,
                      project: ResourceId,
                      number_of_images: int,
                      name: str = None,
                      coordinates: List = None,
                      geometry: Dict = None,
                      area: float = 0,
                      **kwargs) -> Tuple[Flight, Mission]:
        """Create a survey (mission + flight).

        This function is used when images will be attached to the mission.
        As a consequence, a flight will be created as well.
        The survey creation need the bounds of the mission. So, one of
        ``coordinates`` or ``geometry`` (not both) must be sent.

        Args:
            survey_date: Survey date (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            project: Project identifier on which the survey is added.

            number_of_images: Number of photos that will be uploaded.

            name: Optional mission name.

            coordinates: Optional Coordinates bounding the mission to create.
                The last coordinate of the list should be the same as the first one.
                Do not use with ``geometry``.

            geometry: Optional Geometry bounding the mission to create. The geometry
                must be a type "GeometryCollection" with at least one "Polygon" inside.
                Do not use with ``coordinates``.

            area: Optional survey area.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            QueryError: The survey creation response is incorrect.

        Returns:
            Tuple[Flight, Mission]: A tuple with the created flight and mission.

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

        if geometry is not None:
            params_survey['geometry'] = geometry

        if coordinates is not None:
            if geometry is not None:
                raise QueryError('Do not use "coordinates" and "geometry"')
            params_survey['geometry'] = {
                'type': 'GeometryCollection',
                'geometries': [
                    {
                        'type': 'Polygon',
                        'coordinates': [coordinates]
                    }
                ]}

        params_survey.update(kwargs)

        content = self._provider.post(
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

    def describe(self, mission: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a mission or a list of missions.

        Args:
            mission: Identifier of the mission to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The mission description or a list of mission descriptions.

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

    def search(self, *, filter: dict = None, fields: dict = None, limit: int = 100,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search missions.

        Args:
            filter: Optional Search filter (refer to
                ``/search-missions`` definition in the Project
                management API for a detailed description
                of supported operators).

            fields: Optional Field names to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            limit: Optional Maximum number of results to extract (default is ``100``).

            page: Optional Page number (starting at page 1).

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

        Resources: A list of resources OR a namedtuple
                with total number of results and list of resources.

        Examples:
            >>> # search missions with name exacty equals to 'my mission'
            >>> sdk.missions.search(filter={'name': {'$eq': 'my mission'}})
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # search missions having 'my' in their name (case-insensitive)
            >>> sdk.missions.search(filter={'name': {'$match': 'my'}})
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # search missions by IDs (should use missions.describe() instead)
            >>> sdk.missions.search(filter={'_id': {'$eq': '5d6e0dcc965a0f56891f3861'}})
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # search missions of a wanted project (could use '$in' with an array of IDs)
            >>> sdk.projects.search(filter={'project': {'$eq': '41b9b3c7e6cd160006586688'}})
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # search missions related to some flights
            >>> sdk.projects.search(filter={
            ...     'flights': {'$in': ['628a73655029ff0006efe596', '628a73655029ff0006efe597'}
            ... })
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search missions updated after December 15th 2021
            >>> sdk.missions.search(filter={'modification_date': {'$gt': '2021-12-15T00:00:00'}})
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # search missions with a survey date between September and December 2021
            >>> sdk.missions.search(filter={
            ...     'survey_date': {'$gte': '2021-09-01T00:00:00', '$lt': '2022-01-01T00:00:00'}
            ... })
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]

            >>> # get second page of the same search
            >>> sdk.missions.search(filter={...}, page=2)
            [Resource(_id='60924899669e6e0007f8d262'), ...]

            >>> # search 400 last created missions, in 2 calls (prefer search_generator() to get all)
            >>> sdk.missions.search(sort={'creation_date': -1}, limit=200)
            [Resource(_id='5d6e0dcc965a0f56891f3861'), ...]
            >>> sdk.missions.search(sort={'creation_date': -1}, limit=200, page=2)
            [Resource(_id='60924899669e6e0007f8d262'), ...]

            >>> # search missions and also get the total results
            >>> sdk.missions.search(filter={...}, return_total=True)
            ResourcesWithTotal(total=612, results=[Resource(_id='5d6e0dcc965a0f56891f3861'), ...])

        """
        if kwargs.get('missions'):
            raise QueryError('"missions" keyword not exists anymore in missions.search()')
        if kwargs.get('flights'):
            raise QueryError('"flights" keyword not exists anymore in missions.search()')
        if kwargs.get('project'):
            raise QueryError('"project" keyword not exists anymore in missions.search()')
        if kwargs.get('deleted'):
            raise QueryError('"deleted" keyword not exists anymore in missions.search()')
        return search(
            self,
            url='search-missions',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, fields: dict = None,
                         limit: int = 100, page: int = None, sort: dict = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through missions.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found missions are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            filter: Optional ``filter`` dictionary from ``search()`` method.

            fields: Optional ``fields`` dictionary from ``search()`` method.

            limit: Optional maximum number of results by search
                request (default is ``100``).

            page: Optional page number to start the search at (default is 1).

            sort: Optional ``sort`` dictionary from ``search()`` method.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found missions.

        Examples:
            >>> # get all missions matching filter by using generator
            >>> results_iterator = sdk.missions.search_generator(filter={...})
            >>> missions = [r for r in results_iterator]

        """
        return search_generator(self, first_page=1, filter=filter, fields=fields,
                                limit=limit, page=page, sort=sort, **kwargs)

    def delete(self, mission: ResourceId):
        """Delete a mission.

        Args:
            mission: Identifier of the mission to delete.

        """
        self._provider.post(
            path='missions/delete-survey', data={'mission': mission})

    def update_name(self, mission: ResourceId, *, name: str, **kwargs) -> Mission:
        """Update the mission name.

        Args:
            mission: Identifier of the mission to update.

            name: New mission name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Mission: Updated mission resource.
        """
        data = kwargs
        data.update({'mission': mission, 'name': name})
        desc = self._provider.post(path='update-mission-name', data=data)
        return Mission(**desc)

    def update_survey_date(self, mission: ResourceId, *, survey_date: str, **kwargs) -> Mission:
        """Update the mission survey date.

        Args:
            mission: Identifier of the mission to update.

            survey_date: Survey date (format: ``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Mission: Updated mission resource.

        Examples:
            >>> sdk.missions.update_survey_date('5d6e0dcc965a0f56891f3861',
            ...                                 survey_date='2021-11-28')
            Mission(_id='5d6e0dcc965a0f56891f3861')

        """
        data = kwargs
        data.update({'mission': mission, 'survey_date': survey_date})
        desc = self._provider.post(path='update-mission-survey-date', data=data)
        return Mission(**desc)

    def update_geometry(self, mission: ResourceId, *, geometry: dict, **kwargs) -> Mission:
        """Update the mission geometry.

        Args:
            mission: Identifier of the mission to update.

            geometry: GeoJSON Geometry format, needs ``type`` and ``coordinates``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Mission: Updated mission resource.
        """
        if not geometry.get('type'):
            raise QueryError('"geometry.type" must exists')
        if not geometry.get('coordinates'):
            raise QueryError('"geometry.coordinates" must exists')
        data = kwargs
        data.update({'mission': mission, 'geometry': geometry})
        desc = self._provider.post(path='update-mission-geometry', data=data)
        return Mission(**desc)

    def update_bbox(self, mission: ResourceId, *, real_bbox: dict, **kwargs) -> Mission:
        """Update the mission real bbox.

        Args:
            mission: Identifier of the mission to update.

            real_bbox: GeoJSON Geometry, needs ``type`` and ``coordinates``, and an
                optional ``bbox`` with 4-numbers's list (``[minX, minY, maxX, maxY]``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Mission: Updated mission resource.

        Examples:
            >>> sdk.missions.update_bbox('5d6e0dcc965a0f56891f3861', real_bbox={
            ...     'type': 'Polygon',
            ...     'coordinates': [[[112.5, 43.2], [112.6, 43.3], [112.7, 43.1], [112.5, 43.2]]],
            ... })
            Mission(_id='5d6e0dcc965a0f56891f3861')

        """
        if not real_bbox.get('type'):
            raise QueryError('"real_bbox.type" must exists')
        if not real_bbox.get('coordinates'):
            raise QueryError('"real_bbox.coordinates" must exists')

        data = kwargs
        data.update({'mission': mission, 'real_bbox': real_bbox})
        desc = self._provider.post(path='update-mission-bbox', data=data)
        return Mission(**desc)

    def compute_bbox(self, mission: ResourceId, **kwargs) -> Mission:
        """Perform an automatic computation of the mission's bbox.

        Args:
            mission: Identifier of the mission to update.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Mission: Updated mission resource.
        """
        data = kwargs
        data.update({'mission': mission})
        desc = self._provider.post(path='compute-mission-bbox', data=data)
        return Mission(**desc)

    def create_archive(self, mission: ResourceId, *,
                       name: str = None, chunk_size: int = None, **kwargs) -> bool:
        """Request to create an archive of mission's images.

        Args:
            mission: Identifier of the mission.

            name: Optional name of the archive file.

            chunk_size: Optional. Will create files with this maximum size (in MegaBytes).
                Refer to ``/create-mission-archive`` definition in the Project
                management API to have the default chunk value.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            True if creation request is accepted, else False.

        Examples:
            >>> sdk.missions.create_archive('5d6e0dcc965a0f56891f3861', chunk_size=2000)
            True

            >>> sdk.missions.create_archive('5d6e0dcc965a0f56891f3861', name='my custom archive')
            True

        """
        data = kwargs
        data.update({'mission': mission})
        if name is not None:
            data['name'] = name
        if chunk_size is not None:
            data['chunk_size'] = int(chunk_size)
        r = self._provider.post(path='create-mission-archive', data=data)
        if r.get('request') == 'accepted':
            return True
        return False
