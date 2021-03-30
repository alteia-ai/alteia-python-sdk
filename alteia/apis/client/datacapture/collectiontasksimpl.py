from typing import Generator, List

from alteia.apis.provider import CollectionTaskAPI, CollectionTaskManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources


class CollectionTaskImpl:
    def __init__(self, collection_task_api: CollectionTaskAPI,
                 collection_task_management_api: CollectionTaskManagementAPI, **kwargs):
        self._provider = collection_task_api
        self._alt_provider = collection_task_management_api

    def create(self, *, name: str, company: ResourceId, site: ResourceId = None,
               survey: ResourceId = None, location: dict = None,
               forecast_date_range: dict = None, scheduled_date_range: dict = None,
               team: ResourceId = None, pic: ResourceId = None, comment: str = None,
               custom_props: dict = None, requirement: dict = None, purpose: str = None,
               **kwargs) -> Resource:
        """Create a collection task.

        Args:
            name: Collection task name.

            company: Identifier of the company.

            site: Optional site identifier.

            survey: Optional survey identifier.

            location: Optional location
                ``{ adress: {street, zipcode, city},  contact: {name, phone, email}, task_area: {} }``

            forecast_date_range: Optional forecast date range ``{ start_date, end_date}``.

            scheduled_date_range: Optional scheduled date range ``{ start_date, end_date}``.

            team: Optional team identifier.

            pic: Optional pilot in charge identifier.

            comment: Optional comment.

            custom_props: Optional custom properties.

            requirement: Optional requirement.

            purpose: Optional purpose.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A collection task resource.
        """
        data = kwargs
        data.update({
            'name': name,
            'company': company,
        })

        for param_name, param_value in (('site', site),
                                        ('survey', survey),
                                        ('location', location),
                                        ('forecast_date_range', forecast_date_range),
                                        ('scheduled_date_range', scheduled_date_range),
                                        ('team', team),
                                        ('pic', pic),
                                        ('comment',  comment),
                                        ('custom_props', custom_props),
                                        ('requirement', requirement),
                                        ('purpose', purpose),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-task', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, **kwargs
               ) -> List[Resource]:
        """Search collection tasks.

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
            Resources: A list of collection task resources.

        """

        return search(
            self,
            url='search-tasks',
            filter=filter,
            limit=limit,
            page=page,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through collection tasks.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found collection tasks are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found collection tasks.

        """
        return search_generator(self, first_page=0, filter=filter, limit=limit,
                                page=page, **kwargs)

    def describe(self, task: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a collection task.

        Args:
            task: Identifier of the collection task to describe, or list of
                such identifiers.

        Returns:
            Resource: The collection task description
                or a list of collection task descriptions.

        """
        data = kwargs
        if isinstance(task, list):
            data['tasks'] = task
            descs = self._provider.post('describe-tasks', data=data)
            return [Resource(**desc) for desc in descs]
        else:
            data['task'] = task
            desc = self._provider.post('describe-task', data=data)
            return Resource(**desc)

    def delete(self, task: ResourceId, **kwargs):
        """Delete a collection task.

        Args:
            task: Collection task to delete.

        """

        data = kwargs
        data['task'] = task

        self._provider.post('delete-task', data=data)

    def create_flight_log(self, task: ResourceId, **kwargs):
        """Create or update the collection task flight log.

        Args:
            task: Collection task whose flight log needs to be created or updated.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A collection task resource.
        """
        data = kwargs
        data['task'] = task

        self._alt_provider.post('create-or-update-task-flight-log', data=data)

    def rename(self,  task: ResourceId, *, name: str, **kwargs):
        """Rename a collection task.

        Args:
            task: Collection task to rename.

            name: New task name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The renamed collection task.

        """

        data = kwargs
        data.update({'task': task, 'name': name})

        content = self._provider.post('set-task-name', data=data)
        return Resource(**content)

    def update(self, task: ResourceId, *, name: str = None, site: ResourceId = None,
               survey: ResourceId = None, location: dict = None,
               forecast_date_range: dict = None, scheduled_date_range: dict = None,
               team: ResourceId = None, pic: ResourceId = None, comment: str = None,
               custom_props: dict = None, requirement: dict = None, purpose: str = None,
               **kwargs) -> Resource:
        """Update a collection task.

        Args:
            task: Collection task identifier.

            name: Optional collection task name.

            site: Optional site identifier.

            survey: Optional survey identifier.

            location: Optional location
                ``{ adress: {street, zipcode, city},  contact: {name, phone, email}, task_area: {} }``

            forecast_date_range: Optional forecast date range ``{ start_date, end_date}``.

            scheduled_date_range: Optional scheduled date range ``{ start_date, end_date}``.

            team: Optional team identifier.

            pic: Optional pilot in charge identifier.

            comment: Optional comment.

            custom_props: Optional custom properties.

            requirement: Optional requirement.

            purpose: Optional purpose.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A collection task resource.
        """
        data = kwargs
        data['task'] = task

        for param_name, param_value in (('name', name),
                                        ('site', site),
                                        ('survey', survey),
                                        ('location', location),
                                        ('forecast_date_range', forecast_date_range),
                                        ('scheduled_date_range', scheduled_date_range),
                                        ('team', team),
                                        ('pic', pic),
                                        ('comment',  comment),
                                        ('custom_props', custom_props),
                                        ('requirement', requirement),
                                        ('purpose', purpose),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-task', data=data)

        return Resource(**content)
