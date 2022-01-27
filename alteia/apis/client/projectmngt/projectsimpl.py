"""Implementation of projects.

"""
from typing import Generator, List, Union

from alteia.apis.provider import ProjectManagerAPI
from alteia.core.errors import QueryError, ResponseError
from alteia.core.resources.projectmngt.projects import Project
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class ProjectsImpl:
    def __init__(self, project_manager_api: ProjectManagerAPI, **kwargs):
        self._provider = project_manager_api

    def create(self, name: str, company: ResourceId, geometry: dict = None, **kwargs) -> Project:
        """Create a project.

        Args:
            name: Project name.

            company: Company identifier.

            geometry: Optional project geometry.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            QueryError: The project creation response is incorrect.

        Returns:
            Project: A resource encapsulating the created project.

        """
        data = kwargs

        data.update({
            'name': name,
            'company': company
        })

        if geometry is not None:
            data['geometry'] = geometry

        if 'addProjectToUsers' not in data:
            data['addProjectToUsers'] = True

        content = self._provider.post(path='projects', data=data)
        if 'project' not in content:
            raise QueryError('"project" should be in the response content')
        project_desc = content['project']
        return Project(**project_desc)

    def describe(self, project: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a project or a list of projects.

        Args:
            project: Identifier of the project to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The project description or a list of project descriptions.

        """
        data = kwargs
        if isinstance(project, list):
            results = []
            ids_chunks = get_chunks(project, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['projects'] = ids_chunk
                descs = self._provider.post('describe-projects', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['project'] = project
            desc = self._provider.post('describe-project', data=data)
            return Resource(**desc)

    def search(self, *, filter: dict = None, fields: dict = None, limit: int = 100,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search projects.

        Args:
            filter: Optional Search filter (refer to
                ``/search-projects`` definition in the Project
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
            >>> # search projects with name exacty equals to 'my project'
            >>> sdk.projects.search(filter={'name': {'$eq': 'my project'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search projects having 'my' in their name (case-insensitive)
            >>> sdk.projects.search(filter={'name': {'$match': 'my'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search projects having 'my' in their name or place name or tags (case-insensitive)
            >>> sdk.projects.search(filter={'search': {'$match': 'my'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search projects by IDs (should use projects.describe() instead)
            >>> sdk.projects.search(filter={'_id': {'$eq': '5d6e0dcc965a0f56891f3860'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search projects of a wanted company (could use '$in' with an array of IDs)
            >>> sdk.projects.search(filter={'company': {'$eq': '41b9b3c7e6cd160006586688'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # search projects updated after December 15th 2021
            >>> sdk.projects.search(filter={'modification_date': {'$gt': '2021-12-15T00:00:00'}})
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]

            >>> # get second page of the same search
            >>> sdk.projects.search(filter={...}, page=2)
            [Resource(_id='60924899669e6e0007f8d261'), ...]

            >>> # search 400 first projects sorted by name ascending, in 2 calls
            >>> sdk.projects.search(sort={'name': 1}, limit=200)
            [Resource(_id='5d6e0dcc965a0f56891f3860'), ...]
            >>> sdk.projects.search(sort={'name': 1}, limit=200, page=2)
            [Resource(_id='60924899669e6e0007f8d261'), ...]

            >>> # search projects and also get the total results
            >>> sdk.projects.search(filter={...}, return_total=True)
            ResourcesWithTotal(total=940, results=[Resource(_id='5d6e0dcc965a0f56891f3860'), ...])

        """
        if kwargs.get('name'):
            raise QueryError('"name" keyword not exists anymore in projects.search()')
        if kwargs.get('deleted'):
            raise QueryError('"deleted" keyword not exists anymore in projects.search()')
        return search(
            self,
            url='search-projects',
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
        """Return a generator to search through projects.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found projects are sorted chronologically in order to allow
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
            A generator yielding found projects.

        Examples:
            >>> # get all projects matching filter by using generator
            >>> results_iterator = sdk.projects.search_generator(filter={...})
            >>> projects = [r for r in results_iterator]

        """
        return search_generator(self, first_page=1, filter=filter, fields=fields,
                                limit=limit, page=page, sort=sort, **kwargs)

    def update_status(self, project: ResourceId, status: str) -> Project:
        """Update the project status.

        Args:
            project: Identifier of the project to update.

            status: Project status (``pending``, ``available``, ``failed``, ``maintenance``).

        Raises:
            ResponseError : When the project has not been found.

            RuntimeError: The passed status is not allowed.

        Returns:
            Project: Updated project resource.

        """
        available_status = ['pending', 'available', 'failed', 'maintenance']
        if status not in available_status:
            raise RuntimeError(f'Status not in {available_status}')

        data = {'project': project, 'status': status}
        content = self._provider.post(path=f'projects/update/{project}', data=data)

        if project not in str(content):
            raise ResponseError(
                f'Project {project!r} has not been found')
        else:
            d = content.get('project')
            project_resource = Project(**d)
        return project_resource

    def delete(self, project: ResourceId) -> None:
        """Delete the specified Project.

        Args:
            project: Identifier of the project to delete.

        """
        self._provider.delete(path=f'projects/{project}')

    def update_name(self, project: ResourceId, *, name: str, **kwargs) -> Project:
        """Update the project name.

        Args:
            project: Identifier of the project to update.

            name: New project name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.
        """
        data = kwargs
        data.update({'project': project, 'name': name})
        desc = self._provider.post(path='update-project-name', data=data)
        return Project(**desc)

    def update_geometry(self, project: ResourceId, *, geometry: dict, **kwargs) -> Project:
        """Update the project geometry.

        Args:
            project: Identifier of the project to update.

            geometry: GeoJSON Geometry format, needs ``type`` and ``coordinates``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.
        """
        if not geometry.get('type'):
            raise QueryError('"geometry.type" must exists')
        if not geometry.get('coordinates'):
            raise QueryError('"geometry.coordinates" must exists')
        data = kwargs
        data.update({'project': project, 'geometry': geometry})
        desc = self._provider.post(path='update-project-geometry', data=data)
        return Project(**desc)

    def update_bbox(self, project: ResourceId, *, real_bbox: dict, **kwargs) -> Project:
        """Update the project real bbox.

        Args:
            project: Identifier of the project to update.

            real_bbox: GeoJSON Geometry, needs ``type`` and ``coordinates``, and an
                optional ``bbox`` with 4-numbers's list (``[minX, minY, maxX, maxY]``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.

        Examples:
            >>> sdk.projects.update_bbox('5d6e0dcc965a0f56891f3860', real_bbox={
            ...     'type': 'Polygon',
            ...     'coordinates': [[[112.5, 43.2], [112.6, 43.3], [112.7, 43.1], [112.5, 43.2]]],
            ... })
            Project(_id='5d6e0dcc965a0f56891f3860')

        """
        if not real_bbox.get('type'):
            raise QueryError('"real_bbox.type" must exists')
        if not real_bbox.get('coordinates'):
            raise QueryError('"real_bbox.coordinates" must exists')

        data = kwargs
        data.update({'project': project, 'real_bbox': real_bbox})
        desc = self._provider.post(path='update-project-bbox', data=data)
        return Project(**desc)

    def compute_bbox(self, project: ResourceId, **kwargs) -> Project:
        """Perform an automatic computation of the project's bbox.

        Args:
            project: Identifier of the project to update.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.
        """
        data = kwargs
        data.update({'project': project})
        desc = self._provider.post(path='compute-project-bbox', data=data)
        return Project(**desc)

    def update_units(self, project: ResourceId, *, units: dict, **kwargs) -> Project:
        """Update the units of a project.

        Args:
            project: Identifier of the project to update.

            units: Dictionary of different types of units ("distances", "surfaces", "volumes",
                "altitude", "gsd", "weight", "slope").

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.

        Examples:
            >>> sdk.projects.update_units('3037636c9a416900074ac253', units={
            ...     'distances': 'feet',
            ...     'surfaces': 'square-feet',
            ...     'volumes': 'cubic-feet',
            ...     'altitude': 'feet',
            ...     'gsd': 'inch/pixel',
            ...     'weight': 'metric-tons',
            ...     'slope': 'percent',
            ... })
            Project(_id='3037636c9a416900074ac253')
        """

        data = kwargs
        data.update({'project': project, 'units': units})
        desc = self._provider.post(path='update-project-units', data=data)
        return Project(**desc)

    def update_srs(self, project: ResourceId, *,
                   horizontal_srs_wkt: str = None,
                   vertical_srs_wkt: str = None,
                   **kwargs) -> Project:
        """Update the SRS of a project. Horizontal or Vertical or both.

        Args:
            project: Identifier of the project to update.

            horizontal_srs_wkt: Optional WKT of horizontal SRS.

            vertical_srs_wkt: Optional WKT of vertical SRS.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.
        """

        data = kwargs
        data.update({'project': project})
        if horizontal_srs_wkt is not None:
            data['horizontal_srs_wkt'] = horizontal_srs_wkt
        if vertical_srs_wkt is not None:
            data['vertical_srs_wkt'] = vertical_srs_wkt

        desc = self._provider.post(path='update-project-srs', data=data)
        return Project(**desc)

    def update_local_coordinates_dataset(self, project: ResourceId, *,
                                         dataset: ResourceId, **kwargs) -> Project:
        """Update the local coordinates dataset of a project.

        Args:
            project: Identifier of the project to update.

            dataset: Dataset identifier of the local coordinates file.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.
        """

        data = kwargs
        data.update({'project': project, 'local_coords_dataset': dataset})
        desc = self._provider.post(path='update-project-local-coords', data=data)
        return Project(**desc)

    def update_location(self, project: ResourceId, *,
                        location: List[float] = None,
                        fixed: bool = None,
                        **kwargs) -> Project:
        """Update the project's location, set if the project's location is fixed. Or both updates.

        Args:
            project: Identifier of the project to update.

            location: Optional Location in WGS84: (format: ``[Longitude, Latitude]``).
                ``None`` to not change this parameter.

            fixed: Optional Flag to indicate if the location value will be fixed or not.
                ``True`` if you want to fix the position. ``False`` to let the location
                automatically updated in the future. ``None`` to not change this parameter.
                Default: None.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Project: Updated project resource.

        Examples:
            >>> # fix a location of a project. It will not change automatically.
            >>> sdk.projects.update_location('5d6e0dcc965a0f56891f3861',
            ...                              location=[-118.254, 46.95],
            ...                              fixed=True)
            Project(_id='5d6e0dcc965a0f56891f3861')
            >>> # Remove fixed location of a project. It will change automatically.
            >>> sdk.projects.update_location('3037636c9a416900074ac253',
            ...                              fixed=None)
            Project(_id='3037636c9a416900074ac253')

        """

        data = kwargs
        data.update({'project': project})
        if location is not None:
            data['location'] = location
        if fixed is not None:
            data['fixed'] = bool(fixed)

        desc = self._provider.post(path='update-project-location', data=data)
        return Project(**desc)
