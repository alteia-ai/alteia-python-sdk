from typing import List

from alteia.apis.provider import CollectionTaskAPI, CollectionTaskManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources


class CollectionTaskImpl:
    def __init__(self, collection_task_api: CollectionTaskAPI,
                 collection_task_management_api: CollectionTaskManagementAPI, **kwargs):
        self._provider = collection_task_api
        self._alt_provider = collection_task_management_api

    def create(self, *, name: str, company: ResourceId, site: ResourceId = None,
               survey: ResourceId = None, location: dict = None,
               forecast_date_range: dict = None, scheduled_date_range: dict = None,
               team: str = None, pic: ResourceId = None, comment: str = None,
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

            team: Optional team name.

            pic: Optional pilot in charge.

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

        data = kwargs

        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post('search-tasks', data=data)
        results = r.get('results')

        tasks = [Resource(**m) for m in results]

        return tasks

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
