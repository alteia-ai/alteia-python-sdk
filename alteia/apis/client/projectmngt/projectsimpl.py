"""Implementation of projects.

"""
from typing import List, Optional

from alteia.apis.provider import ProjectManagerAPI, UIServicesAPI
from alteia.core.errors import QueryError, ResponseError
from alteia.core.resources.projectmngt.projects import Project
from alteia.core.utils.typing import ResourceId


class ProjectsImpl:
    def __init__(self, project_manager_api: ProjectManagerAPI,
                 ui_services_api: UIServicesAPI, **kwargs):
        self._provider = project_manager_api
        self._alt_provider = ui_services_api

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

        content = self._alt_provider.post(path='projects', data=data)
        if 'project' not in content:
            raise QueryError('"project" should be in the response content')
        project_desc = content['project']
        return Project(**project_desc)

    def search(self, *, name: str = None, deleted: bool = False,
               **kwargs) -> List[Project]:
        """Search for projects.

        Args:
            name: Optional name of the project *(the comparison is case insensitive)*.
                Default: ``*`` to search all the projects.

            deleted: Optional parameter to search for deleted project or not
                (``False`` by default).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Raises:
            QueryError : When the response is not consistent.

        Returns:
            [Project]: List of project resources matching the search criteria.

        Examples:
            Get the projects with a specific name (name is not unique):

            >>> sdk.projects.search(name='My_project')
            [<alteia.core.resources.projectmngt.projects.Project...>, ...]

            Get all the projects available:

            >>> sdk.projects.search()
            [<alteia.core.resources.projectmngt.projects.Project...>, ...]

        """
        data = kwargs
        if name is None:
            name = '*'
        data.update({'search': name, 'deleted': deleted})
        content = self._alt_provider.post(path='projects/search', data=data)

        if 'projects' not in content:
            raise QueryError(
                '"projects" item should be in the response content')

        return [Project(**d) for d in content['projects']]

    def describe(self, project: ResourceId,
                 deleted: bool = False) -> Optional[Project]:
        """Describe the project for the specified id.

        Args:
            project: Project identifier.

            deleted: Optional parameter to describe a deleted project or not
                (``False`` by default).

        Returns:
            Project: Project resource matching the id (``None`` if not found).

        Examples:
            >>> sdk.projects.describe('5ce7f379327e9d5f15e37bb4')
            <alteia.core.resources.projectmngt.projects.Project ...>

        """
        try:
            content = self._alt_provider.post(path=f'projects/{project}',
                                              data={'deleted': deleted})
        except ResponseError:
            # When a project is not found, a 404 response is returned
            content = None

        if project not in str(content):
            project_resource = None
        else:
            d = content.get('project')
            project_resource = Project(**d)
        return project_resource

    def update_status(self, project: ResourceId, status: str) -> Project:
        """Update the project status.

        Args:
            project: Project identifier.

            status: Project status (``pending``, ``available``, ``failed``).

        Raises:
            ResponseError : When the project has not been found.

            RuntimeError: The passed status is not allowed.

        Returns:
            Project: Updated project resource.

        """
        available_status = ['pending', 'available', 'failed']
        if status not in available_status:
            raise RuntimeError('Status not in {}'.format(available_status))

        data = {'project': project, 'status': status}
        content = self._alt_provider.post(path=f'projects/update/{project}', data=data)

        if project not in str(content):
            raise ResponseError(
                'Project {!r} has not been found'.format(project))
        else:
            d = content.get('project')
            project_resource = Project(**d)
        return project_resource

    def delete(self, project: ResourceId) -> None:
        """Delete the specified Project.

        Args:
            project: Identifier of the project to delete.

        """
        self._alt_provider.delete(path=f'projects/{project}')

    def rename(self, project: ResourceId, *, name: str, **kwargs) -> Project:
        """Rename the given project.

        Args:
            project: Project identifier.

            name: Name to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        data['name'] = name

        content = self._alt_provider.put(path=f'projects/{project}', data=data)
        return Project(**content)
