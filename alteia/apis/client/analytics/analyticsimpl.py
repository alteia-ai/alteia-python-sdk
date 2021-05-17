"""Analytics implementation
"""

from collections import defaultdict
from typing import Dict, Generator, List, Union

from alteia.apis.provider import AnalyticsServiceAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import ResourceId


class AnalyticsImpl:
    def __init__(self, analytics_service_api: AnalyticsServiceAPI, **kwargs):
        self._provider = analytics_service_api

    def share_with_company(self, analytic: ResourceId, *,
                           company: ResourceId, **kwargs):
        """Allow a company to view, order, etc. the analytic.

        Args:
            analytic: Identifier of the analytic to update.

            company: Identifier of the company to share the analytic with.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = {'analytic': analytic,
                'company': company}
        data.update(kwargs)
        self._provider.post(path='share-analytic-with-company', data=data)

    def unshare_with_company(self, analytic: ResourceId, *,
                             company: ResourceId, **kwargs):
        """Stop sharing the analytic with a company.

        Args:
            analytic: Identifier of the analytic to update.

            company: Identifier of the company to stop sharing the analytic with.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = {'analytic': analytic,
                'company': company}
        data.update(kwargs)
        self._provider.post(path='unshare-analytic-with-company', data=data)

    def search(self, *, name: str = None, filter: Dict = None,
               limit: int = None, page: int = None, sort: dict = None,
               return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search for a list of analytics.

        Args:
            name: Analytic name.

            filter: Search filter dictionary (refer to ``/search-analytics``
                definition in the Analytics-service API for a detailed description
                of ``filter``).

            limit: Maximum number of results to extract.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Analytics: A list of analytics resources OR a namedtuple
                with total number of results and list of analytics resources.

        """
        data = kwargs

        for prop_name, value in [('filter', filter or {}),
                                 ('limit', limit),
                                 ('page', page),
                                 ('sort', sort)]:
            if value is not None:
                data.update({prop_name: value})

        if name is not None:
            data['filter']['name'] = {'$eq': name}

        search_desc = self._provider.post(
            path='search-analytics', data=data, as_json=True)

        analytics = search_desc.get('results')

        results = [Resource(**analytic) for analytic in analytics]

        if return_total is True:
            total = search_desc.get('total')
            return ResourcesWithTotal(total=total, results=results)
        else:
            return results

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through analytics.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found analytics are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found analytics.

        """
        return search_generator(self, first_page=0, filter=filter, limit=limit,
                                page=page, **kwargs)

    def describe(self, analytic: ResourceId, **kwargs) -> Resource:
        """Describe an analytic.

        Args:
            analytic: Identifier of the analytic to describe.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The analytic description.

        """
        data = kwargs

        data['analytic'] = analytic
        desc = self._provider.post('describe-analytic', data=data)
        return Resource(**desc)

    def create(self, *, name: str, version: str, docker_image: str,
               company: ResourceId,
               display_name: str = None, description: str = None,
               instance_type: str = None, volume_size: int = None,
               inputs: List[dict] = None, parameters: List[dict] = None,
               deliverables: List[dict] = None, outputs: List[dict] = None,
               tags: List[str] = None, groups: List[str] = None,
               **kwargs) -> Resource:
        """Create an analytic.

        Args:
            name: Analytic name (must be unique with the version).

            version: Analytic version in semver format (must be unique with the name)

            docker_image: Docker image used for the analytic computation,
                including the Docker registry address.
                (example: ``"gcr.io/myproject/myanalytic:v1.0"``).

            company: Id of the company owning the analytic.

            display_name: Optional user-friendly name of the analytic.

            description: Optional analytic description.

            instance_type: Optional instance type on which the analytic
                will be run (example: ``"small"``).

            volume_size: Optional size of the attached volume (in gigabytes).

            inputs: Optional inputs of the analytic.

            parameters: Optional parameters of the analytic.

            deliverables: Optional deliverables of the analytic.

            outputs: Optional outputs of the analytic.

            tags: Optional tags of the analytic.

            groups: Optional groups of the analytic (used by the analytic
                catalogue on the front-end to group analytics).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created analytic description.

        Raise:
            KeyError: When a passed value is not supported.

        Examples:
            >>> sdk.analytics.create(name="my_vehicle_detection",
            ...     version="0.0.1",
            ...     display_name="Vehicle detection",
            ...     description="Detects vehicles in orthomosaic images",
            ...     docker_image="gcr.io/myproject/vehicule-detection:v1.0",
            ...     company="5d3714e14c50356e2abd1f97",
            ...     instance_type='large',
            ...     volume_size=50,
            ...     inputs=[{
            ...         "name": "ortho",
            ...         "display_name": "Orthomosaic",
            ...         "description": "Orthomosaic",
            ...         "scheme": {
            ...             "type": "string", "pattern": "^[0-9a-f]{24}$"
            ...         },
            ...         "source": {
            ...             "service": "data-manager", "resource": "dataset",
            ...             "scheme": {
            ...                 "type": "object",
            ...                 "properties": {"type": {"const": "raster"}},
            ...                 "required": ["type"]
            ...             },
            ...         },
            ...         "required": True
            ...     }],
            ...     parameters=[{
            ...         "name": "project",
            ...         "display_name": "Project",
            ...         "description": "Project identifier",
            ...         "required": True,
            ...         "scheme": {
            ...             "type": "string", "pattern": "^[0-9a-f]{24}$"
            ...         }
            ...      }],
            ...     deliverables=[{
            ...         "name": "positions",
            ...         "display_name": "Vehicule positions",
            ...         "description": "Position of the vehicules in a CSV",
            ...         "scheme": {
            ...             "type": "string", "pattern": "^[0-9a-f]{24}$"
            ...         },
            ...         "source": {
            ...             "service": "data-manager", "resource": "dataset",
            ...             "scheme": {
            ...                 "type": "object",
            ...                 "properties": {"type": {"const": "file"}},
            ...                 "required": ["type"]
            ...             },
            ...         },
            ...         "required": True
            ...     }],
            ...      tags=["vehicle_detection"],
            ...      groups=["GeoInt"])
            <alteia.core.resources.Resource with id ... (analytic)>

        """
        data = defaultdict(dict)
        data.update(kwargs)

        data['name'] = name
        data['version'] = version
        data['company'] = company
        data['algorithm']['docker_image'] = docker_image

        if instance_type:
            data['instance']['type'] = instance_type
        if volume_size:
            data['instance']['volume'] = volume_size

        for k, v in [
            ('display_name', display_name),
            ('description', description),
            ('inputs', inputs), ('parameters', parameters),
            ('deliverables', deliverables), ('outputs', outputs),
            ('tags', tags), ('groups', groups)
        ]:
            if v:
                data.update({k: v})

        desc = self._provider.post(
            path='create-analytic', data=dict(data), as_json=True)

        return Resource(**desc)

    def delete(self, analytic: Union[ResourceId, List[ResourceId]], **kwargs) -> None:
        """Delete an analytic or a list of analytics permanently.

        Args:
            analytic: Analytic identifier (or list of identifiers) to delete.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        if not isinstance(analytic, list):
            analytic_list = [analytic]
        else:
            analytic_list = analytic

        for analytic in analytic_list:
            data = {'analytic':  analytic}
            data.update(kwargs)

            self._provider.post(
                path='delete-analytic-permanently',
                data=data,
                as_json=False
            )

    def order(self, analytic: ResourceId, *, inputs: dict = None,
              parameters: dict = None, deliverables: List[str] = None,
              project: ResourceId = None, mission: ResourceId = None,
              **kwargs) -> Resource:
        """Order an analytic.

        Args:
            analytic: Identifier of the analytic to order.

            inputs: Optional inputs of the analytic.

            parameters: Optional parameters of the analytic.

            deliverables: List of optional deliverables to generate.
                When empty or ``None`` only required deliverables are generated.

            project: Optional project of the analytic.

            mission: Optional mission of the analytic.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created ``product`` description.

        Examples:
            >>> sdk.analytics.order(analytic='5d5a73b58cf5360006397aa0',
            ...     inputs={"ortho": "5d3714e14c50356e2abd1f97"},
            ...     deliverables=["vehicles"],
            ...     parameters={"project": "5d3195209755b0349d0539ad"},
            ...     project='5d3195209755b0349d0539ad')
            <alteia.core.resources.Resource with id ... (product)>

        """
        data = {'analytic': analytic}

        # Update to the format expected by analytics-service
        if deliverables:
            deliverables = {d: None for d in deliverables}

        for k, v in [('inputs', inputs), ('parameters', parameters),
                     ('deliverables', deliverables),
                     ('project', project), ('mission', mission)]:
            if v:
                data.update({k: v})

        data.update(kwargs)

        desc = self._provider.post(path='order-analytic', data=data)

        return Resource(**desc)
