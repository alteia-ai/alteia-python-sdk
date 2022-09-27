from typing import Any, Dict, Generator, Iterable, List, Union

from alteia.apis.provider import FeaturesServiceAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class FeaturesImpl:
    def __init__(self, features_service_api: FeaturesServiceAPI, **kwargs):
        self._provider = features_service_api

    def create(self, *, geometry: dict = None, properties: dict = None,
               collection: ResourceId = None, **kwargs) -> Resource:
        """Create a feature.

        Args:
            geometry: A dictionary following GeoJSON specification.

            properties: Dictionary of properties.

            collection: Identifier of a collection to add the created
                feature to.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource for the created feature.

        """
        data = kwargs

        if geometry is not None:
            data['geometry'] = geometry

        if collection is not None:
            data['collection'] = collection

        if properties is not None:
            data['properties'] = properties

        desc = self._provider.post('create-feature', data=data)
        return Resource(**desc)

    def create_features(self, descriptions: Iterable[dict],
                        **kwargs) -> List[Resource]:
        """Create features.

        Args:
            descriptions: List of features descriptions, each
                description is a dictionary with keys among arguments
                of ``create()``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            List of resource for the created features.

        """
        data = kwargs
        data['features'] = descriptions
        descs = self._provider.post('create-features', data=data)
        return [Resource(**desc)
                for desc in descs]

    def update_feature_properties(
            self,
            feature: ResourceId,
            properties: Dict[str, Any]
    ) -> Resource:
        """Update feature properties

        Args:
            feature: The feature id.
            properties: The dictionary of properties to update.

        Returns:
            The updated feature resource.
        """
        desc = self._provider.post(
            'update-feature-properties',
            data={'feature': feature, 'properties': properties}
        )
        return Resource(**desc)

    def update_features_properties(
            self,
            features_properties: Dict[ResourceId, Dict]
    ) -> List[Resource]:
        """Update features properties

        Args:
            features_properties: Map : featureId -> properties description.

        Returns:
            List of updated features resources.
        """
        descs = self._provider.post(
            'update-features-properties',
            data=features_properties
        )
        return [Resource(**desc)
                for desc in descs]

    def delete_feature_properties(
            self,
            feature: ResourceId,
            properties: List[str]
    ) -> Resource:
        """Delete feature properties

        Args:
            feature: The feature id.
            properties: List of properties to delete.

        Returns:
            The updated feature resource.
        """
        desc = self._provider.post(
            'delete-feature-properties',
            data={'feature': feature, 'properties': properties}
        )
        return Resource(**desc)

    def delete_features_properties(
            self,
            features_properties: Dict[ResourceId, List[str]]
    ) -> List[Resource]:
        """Delete features properties

        Args:
            features_properties: The dictionary key is the feature ID and
                its value is the list of properties to remove.

        Returns:
            List of updated features resources.
        """
        descs = self._provider.post(
            'delete-features-properties',
            data=features_properties
        )
        return [Resource(**desc)
                for desc in descs]

    def describe(self, feature: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a feature or a list of features.

        Args:
            feature: Identifier of the feature to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The feature description or a list of feature description.

        """
        data = kwargs
        if isinstance(feature, list):
            results = []
            ids_chunks = get_chunks(feature, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['features'] = ids_chunk
                descs = self._provider.post('describe-features', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['feature'] = feature
            desc = self._provider.post('describe-feature', data=data)
            return Resource(**desc)

    def delete(self, feature: SomeResourceIds, *, permanent: bool = False,
               **kwargs):
        """Delete a feature or multiple features.

        Args:
            feature: Identifier of the feature to delete, or list of
                such identifiers.

            permanent: Whether to delete features permanently or not.
                Default to False.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if isinstance(feature, list):
            path = 'delete-features' if not permanent \
                else 'delete-features-permanently'
            ids_chunks = get_chunks(feature, self._provider.max_per_delete)
            for ids_chunk in ids_chunks:
                data['features'] = ids_chunk
                self._provider.post(path, data=data, as_json=False)
        else:
            path = 'delete-feature' if not permanent \
                else 'delete-feature-permanently'
            data['feature'] = feature
            self._provider.post(path, data=data, as_json=False)

    def restore(self, feature: SomeResourceIds, **kwargs):
        """Restore a feature or multiple features.

        Args:
            feature: Identifier of the feature to restore, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if isinstance(feature, list):
            path = 'restore-features'
            data['features'] = feature
        else:
            path = 'restore-feature'
            data['feature'] = feature

        self._provider.post(path=path, data=data, as_json=True)

    def set_geometry(self, feature: ResourceId, *, geometry: dict,
                     **kwargs):
        """Set the geometry of the feature.

        Args:
            feature: Identifier of the feature whose geometry to set.

            geometry: A dictionary following GeoJSON specification.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'feature': feature,
                     'geometry': geometry})
        self._provider.post(path='set-feature-geometry', data=data)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs
               ) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search features.

        Args:
            filter: Search filter dictionary (refer to ``/search-features``
                definition in the Feature Service API for a detailed description
                of ``filter``).

            limit: Optional Maximum number of results to extract.

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

        Returns:
            A list of features descriptions OR a namedtuple
            with total number of results and list of features descriptions.

        Examples:
            >>> sdk.features.search(filter={'collection': {'$eq': '5f5155ae8dcb064fcbf4ae35'}})
            [Resource(_id='5f5155ae8dcb064fcbf4ae35'), ...]

            >>> sdk.features.search(filter={'properties.name': {'$eq': 'Truck'}},
            ...                     return_total=True)
            ResourcesWithTotal(
                total=...,
                results=[Resource(_id='5f5155ae8dcb064fcbf4ae35'), ...]
            )

        """
        data = kwargs

        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post('search-features', data=data)

        features = r.get('results')

        results = [Resource(**feature) for feature in features]

        if return_total is True:
            total = r.get('total')
            return ResourcesWithTotal(total=total, results=results)
        else:
            return results

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through features.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found features are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 1).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found features.

        """
        return search_generator(self, first_page=1, filter=filter, limit=limit,
                                page=page, **kwargs)

    def add_attachments(self, *, feature: ResourceId, attachments: List[ResourceId],
                        **kwargs):
        """Add attachments to a feature

        Args:
            feature: Identifier of the feature.

            attachments: List datasets.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'feature': feature,
                     'attachments': attachments})
        self._provider.post(path='add-attachments', data=data)

    def remove_attachments(self, *, feature: ResourceId, attachments: List[ResourceId],
                           **kwargs):
        """Remove attachments to a feature

        Args:
            feature: Identifier of the feature.

            attachments: List datasets.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'feature': feature,
                     'attachments': attachments})
        self._provider.post(path='remove-attachments', data=data)
