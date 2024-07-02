from typing import Generator, List, Union

from alteia.apis.provider import SeasonPlannerTrialManagementAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search, search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class TrialsImpl:
    def __init__(self, season_planner_trial_management_api: SeasonPlannerTrialManagementAPI,
                 **kwargs):
        self._provider = season_planner_trial_management_api

    def create(self, *, field: ResourceId, name: str, crop: ResourceId, comment: str = None,
               season: str = None, location: dict = None, missions: List = None, links: List = None,
               custom_id: ResourceId = None, **kwargs) -> Resource:
        """Create a trial.

        Args:
            field: Field identifier

            name: Field name.

            crop: Crop identifier.

            comment: Optional comment.

            season: The year of the trial (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            location: Optional location
                ``{    "crs": {
                            "type": "name",
                            "properties": {
                                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                            }
                        },
                        "type": "Feature",
                        "geometry":
                        {

                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    -1.201407,
                                    44.154277,
                                    0
                                ],
                                [
                                    -1.200717,
                                    44.155139,
                                    0
                                ],
                                [
                                    -1.202496,
                                    44.155113,
                                    0
                                ],
                                [
                                    -1.201407,
                                    44.154277,
                                    0
                                ]
                            ]
                        ],
                        "bbox": [
                            -1.140019,
                            44.154956,
                            -1.136312,
                            44.157271
                        ]
                    }}``

            missions: Optional missions will be added to the trial and returned in the response.
                    ``[
                        {
                            "name": "string",
                            "start_date": "2019-08-24T14:15:22Z",
                            "end_date": "2019-08-24T14:15:22Z",
                            "description": "string",
                            "estimation_methods": [
                                "5f02f308a6f7f53d73962efa"
                            ],
                            "growth_stages_range": {
                                "from": "5f031dd9a6f7f53d73962efb",
                                "to": "5f031dd9a6f7f53d73962efb"
                            }
                        }
                    ]``

            links: Optional trials linked to this trial.
                   Linked trials must all have the same field.

            custom_id: Optional custom id.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A trial resource.
        """
        data = kwargs
        data.update({
            'field': field,
            'name': name,
            'crop': crop,
        })

        for param_name, param_value in (('comment', comment),
                                        ('season', season),
                                        ('location', location),
                                        ('missions', missions),
                                        ('links', links),
                                        ('custom_id', custom_id),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-trial', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search trials.

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
                        "field": {
                            "$eq": "string"
                        },
                        "crop": {
                            "$eq": "string"
                        },
                        "season": {
                            "$eq": "2019-08-24T14:15:22Z"
                        }
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
            Resources: A list of trial resources.

        """

        return search(
            self,
            url='search-trials',
            filter=filter,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through trials.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found trials are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found trials.

        """
        return search_generator(self, first_page=0, filter=filter, limit=limit,
                                page=page, **kwargs)

    def describe(self, trial: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a trial.

        Args:
            trial: Identifier of the trial to describe, or list of
                such identifiers.

        Returns:
            Resource: The trial description
                or a list of trial descriptions.

        """
        data = kwargs
        if isinstance(trial, list):
            results = []
            ids_chunks = get_chunks(trial, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['trials'] = ids_chunk
                descs = self._provider.post('describe-trials', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['trial'] = trial
            desc = self._provider.post('describe-trial', data=data)
            return Resource(**desc)

    def delete(self, trial: ResourceId, **kwargs):
        """Delete a trial.

        Args:
            trial: trial to delete.

        """

        data = kwargs
        data['trial'] = trial

        self._provider.post('delete-trial', data=data)

    def update(self, trial: ResourceId, field: ResourceId, crop: ResourceId, name: str = None,
               comment: str = None, season: str = None, location: dict = None,
               links: List = None, custom_id: ResourceId = None, **kwargs) -> Resource:
        """Update a trial.

        Args:
            trail: Trial identifier.

            field: Field identifier.

            crop: Crop identifier.

            name: Field name.

            comment: Optional comment.

            season: The year of the trial (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            location: Optional location
                ``{    "crs": {
                            "type": "name",
                            "properties": {
                                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                            }
                        },
                        "type": "Feature",
                        "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    -1.201407,
                                    44.154277,
                                    0
                                ],
                                [
                                    -1.200717,
                                    44.155139,
                                    0
                                ],
                                [
                                    -1.202496,
                                    44.155113,
                                    0
                                ],
                                [
                                    -1.201407,
                                    44.154277,
                                    0
                                ]
                            ]
                        ],
                        "bbox": [
                            -1.140019,
                            44.154956,
                            -1.136312,
                            44.157271
                        ]
                    }}``

            links: Optional trials linked to this trial.
                   Linked trials must all have the same field.

            custom_id: Optional custom id.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A trial resource.
        """
        data = kwargs
        data['trial'] = trial
        data['field'] = field
        data['crop'] = crop

        for param_name, param_value in (('name', name),
                                        ('comment', comment),
                                        ('season', season),
                                        ('location', location),
                                        ('links', links),
                                        ('custom_id', custom_id),):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='update-trial', data=data)

        return Resource(**content)

    def set_plots_on_trial(self, *, trial: ResourceId, plots: dict, **kwargs) -> Resource:
        """
        Set plots or microplots on a trial

        Args:
            trial: Trial identifier.

            plots: The (micro-)plots be added to the trial.
                ``{
                    "location": {
                        "crs": {
                            "type": "name",
                            "properties": {
                                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                            }
                        },
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                    [
                                        [
                                            -1.201407,
                                            44.154277,
                                            0
                                        ],
                                        [
                                            -1.200717,
                                            44.155139,
                                            0
                                        ],
                                        [
                                            -1.202496,
                                            44.155113,
                                            0
                                        ],
                                        [
                                            -1.201407,
                                            44.154277,
                                            0
                                        ]
                                ],
                            ],
                        "bbox": [
                            -1.140019,
                            44.154956,
                            -1.136312,
                            44.157271
                        ]
                        },
                    "id": 0,
                    "properties": { }
                    },
                    "name": "string"
                }``

        Returns:
            Resource: A trial resource.
        """
        data = kwargs
        data["trial"] = trial
        data["plots"] = plots

        content = self._provider.post(path='set-plots-on-trial', data=data)

        return Resource(**content)

    def set_dtm_dataset_on_trial(self, *, trial: ResourceId, dataset: ResourceId,
                                 **kwargs) -> Resource:
        """
        Set trial DTM dataset on a trial

        Args:
            trial: Trial identifier.

            dataset: Dataset identifier.

        Returns:
            Resource: A trial resource.
        """
        data = kwargs
        data["trial"] = trial
        data["dataset"] = dataset

        content = self._provider.post(path='set-dtm-dataset-on-trial', data=data)

        return Resource(**content)
