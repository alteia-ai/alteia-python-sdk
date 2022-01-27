from typing import Generator, List, Union

from alteia.apis.provider import ProjectManagerAPI
from alteia.core.errors import QueryError
from alteia.core.resources.projectmngt.flights import Flight
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class FlightsImpl:
    def __init__(self, project_manager_api: ProjectManagerAPI, **kwargs):
        self._provider = project_manager_api

    def create(self, *args, **kwargs):
        raise NotImplementedError('missions.create() must be used instead')

    def describe(self, flight: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a flight or a list of flights.

        Args:
            flight: Identifier of the flight to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The flight description or a list of flight descriptions.

        """
        data = kwargs
        if isinstance(flight, list):
            results = []
            ids_chunks = get_chunks(flight, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['flights'] = ids_chunk
                descs = self._provider.post('describe-flights', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['flight'] = flight
            desc = self._provider.post('describe-flight', data=data)
            return Resource(**desc)

    def describe_uploads_status(self, *,
                                flights: SomeResourceIds = None,
                                missions: SomeResourceIds = None,
                                projects: SomeResourceIds = None,
                                limit: int = None, page: int = None,
                                return_total: bool = False,
                                **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Describe uncompleted flights status, descending sort by flight creation date.

        Args:
            flights: Optional Identifier of a flight or list of such identifiers.

            missions: Optional Identifier of a mission or list of such identifiers.

            projects: Optional Identifier of a project or list of such identifiers.

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 1).

            return_total: Optional Return the number of results found, default ``False``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A list of flights OR a namedtuple with total number of results and list of flights.
        """
        if flights is not None and not isinstance(flights, list):
            flights = [flights]
        if missions is not None and not isinstance(missions, list):
            missions = [missions]
        if projects is not None and not isinstance(projects, list):
            projects = [projects]
        data = kwargs
        for name, value in [('flights', flights),
                            ('missions', missions),
                            ('projects', projects),
                            ('page', page),
                            ('limit', limit)]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post('describe-flight-uploads-status', data=data)
        descriptions = r.get('results')
        results = [Resource(id=desc.get('flight'), **desc) for desc in descriptions]

        if return_total is True:
            total = r.get('total')
            return ResourcesWithTotal(total=total, results=results)
        return results

    def search(self, *, filter: dict = None, fields: dict = None, limit: int = 100,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search flights.

        Args:
            filter: Optional Search filter (refer to
                ``/search-flights`` definition in the Project
                management API for a detailed description
                of supported operators).

            fields: Optional Field names to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            limit: Optional Maximum number of results to extract (default is ``100``).

            page: Optional Page number (starting at page 1).

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

        Examples:
            >>> # search flights by IDs (should use flights.describe() instead)
            >>> sdk.flights.search(filter={'_id': {'$eq': '5d6e0dcc965a0f56891f3865'}})
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # search flights of a wanted project (could use '$in' with an array of IDs)
            >>> sdk.flights.search(filter={'project': {'$eq': '41b9b3c7e6cd160006586688'}})
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # search flights of wanted missions
            >>> sdk.flights.search(filter={
            ...     'mission': {'$in': ['5d6e0dcc965a0f56891f3861', '60924899669e6e0007f8d262'}
            ... })
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # search flights updated after December 15th 2021
            >>> sdk.flights.search(filter={'modification_date': {'$gt': '2021-12-15T00:00:00'}})
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # search flights having 1000+ photos
            >>> sdk.flights.search(filter={'number_of_photos': {'$gte': 1000}})
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # search uncompleted flights of wanted mission (prefer describe_uploads_status())
            >>> sdk.flights.search(filter={
            ...     'status.name': {'$ne': 'completed'},
            ...     'mission': {'eq': '5d6e0dcc965a0f56891f3861'},
            ... })
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]

            >>> # get second page of the same search
            >>> sdk.flights.search(filter={...}, page=2)
            [Resource(_id='60924899669e6e0007f8d266'), ...]

            >>> # search 400 last created flights, in 2 calls (prefer search_generator() to get all)
            >>> sdk.flights.search(sort={'creation_date': -1}, limit=200)
            [Resource(_id='5d6e0dcc965a0f56891f3865'), ...]
            >>> sdk.flights.search(sort={'creation_date': -1}, limit=200, page=2)
            [Resource(_id='60924899669e6e0007f8d266'), ...]

            >>> # search flights and also get the total results
            >>> sdk.flights.search(filter={...}, return_total=True)
            ResourcesWithTotal(total=612, results=[Resource(_id='5d6e0dcc965a0f56891f3865'), ...])

        """
        if kwargs.get('project'):
            raise QueryError('"project" keyword not exists anymore in flights.search()')
        if kwargs.get('mission'):
            raise QueryError('"mission" keyword not exists anymore in flights.search()')
        return search(
            self,
            url='search-flights',
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
        """Return a generator to search through flights.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found flights are sorted chronologically in order to allow
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
            A generator yielding found flights.

        Examples:
            >>> # get all flights matching filter by using generator
            >>> results_iterator = sdk.flights.search_generator(filter={...})
            >>> flights = [r for r in results_iterator]

        """
        return search_generator(self, first_page=1, filter=filter, fields=fields,
                                limit=limit, page=page, sort=sort, **kwargs)

    def update_name(self, flight: ResourceId, *, name: str, **kwargs) -> Flight:
        """Update the flight name.

        Args:
            flight: Identifier of the flight to update.

            name: New flight name.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Flight: Updated flight resource.
        """
        data = kwargs
        data.update({'flight': flight, 'name': name})
        desc = self._provider.post(path='update-flight-name', data=data)
        return Flight(**desc)

    def update_survey_date(self, flight: ResourceId, *, survey_date: str, **kwargs) -> Flight:
        """Update the flight survey date.

        Args:
            flight: Identifier of the flight to update.

            survey_date: Survey date (format: ``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Flight: Updated flight resource.

        Examples:
            >>> sdk.flights.update_survey_date('5d6e0dcc965a0f56891f3865',
            ...                                survey_date='2021-11-28')
            Flight(_id='5d6e0dcc965a0f56891f3865')

        """
        data = kwargs
        data.update({'flight': flight, 'survey_date': survey_date})
        desc = self._provider.post(path='update-flight-survey-date', data=data)
        return Flight(**desc)

    def update_geodata(self, flight: ResourceId, *,
                       bbox: list = None, geometry: dict = None, **kwargs) -> Flight:
        """Update the flight geo data (bbox and geometry).

        Args:
            flight: Identifier of the flight to update.

            bbox: Optional 4-numbers's list (``[minX, minY, maxX, maxY]``).

            geometry: Optional GeoJSON Geometry, needs ``type`` and ``coordinates``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Flight: Updated flight resource.
        """
        if geometry is not None:
            if not geometry.get('type'):
                raise QueryError('"geometry.type" must exists')
            if not geometry.get('coordinates'):
                raise QueryError('"geometry.coordinates" must exists')
        data = kwargs
        data['flight'] = flight

        if 'data' not in data:
            data.update({'data': {}})

        for name, value in [('bbox', bbox),
                            ('geometry', geometry)]:
            if value is not None:
                data['data'].update({name: value})
        desc = self._provider.post(path='update-flight-data', data=data)
        return Flight(**desc)

    def update_bbox(self, flight: ResourceId, *, real_bbox: dict, **kwargs) -> Flight:
        """Update the flight real bbox.

        Args:
            flight: Identifier of the flight to update.

            real_bbox: GeoJSON Geometry, needs ``type`` and ``coordinates``, and an
                optional ``bbox`` with 4-numbers's list (``[minX, minY, maxX, maxY]``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Flight: Updated flight resource.

        Examples:
            >>> sdk.flights.update_bbox('5d6e0dcc965a0f56891f3865', real_bbox={
            ...     'type': 'Polygon',
            ...     'coordinates': [[[112.5, 43.2], [112.6, 43.3], [112.7, 43.1], [112.5, 43.2]]],
            ... })
            Flight(_id='5d6e0dcc965a0f56891f3865')

        """
        if not real_bbox.get('type'):
            raise QueryError('"real_bbox.type" must exists')
        if not real_bbox.get('coordinates'):
            raise QueryError('"real_bbox.coordinates" must exists')

        data = kwargs
        data.update({'flight': flight, 'real_bbox': real_bbox})
        desc = self._provider.post(path='update-flight-bbox', data=data)
        return Flight(**desc)

    def update_status(self, flight: ResourceId, *, status: str, **kwargs) -> Flight:
        """Update the flight status.

        Args:
            flight: Identifier of the flight to update.

            status: Upload status (one of: ``flying``, ``uploading``,
                ``temporary-blocked``, ``error``, ``completed``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Flight: Updated flight resource.
        """
        data = kwargs
        data.update({'flight': flight, 'status': status})
        desc = self._provider.post(path='update-flight-status', data=data)
        return Flight(**desc)
