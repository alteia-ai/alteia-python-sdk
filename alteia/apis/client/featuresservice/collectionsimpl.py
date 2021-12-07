import os
from typing import Iterable, List

from alteia.apis.provider import FeaturesServiceAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources


class CollectionsImpl:
    def __init__(self, features_service_api: FeaturesServiceAPI, **kwargs):
        self._provider = features_service_api

    def create(self, *, name: str = None, features: List[ResourceId] = None,
               properties: dict = None, schema: dict = None,
               **kwargs) -> Resource:
        """Create a collection.

        Args:
            name: The name of the collection to create.

            features: List of feature identifiers.

            properties: Dictionary of properties.

            schema: JSON schema of the collection.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource for the created collection.

        """
        data = kwargs

        if name is not None:
            data['name'] = name

        if features is not None:
            data['features'] = features

        if properties is not None:
            data['properties'] = properties

        if schema is not None:
            data['schema'] = schema

        desc = self._provider.post('create-collection', data=data)
        return Resource(**desc)

    def create_collections(self, descriptions: Iterable[dict],
                           **kwargs) -> List[Resource]:
        """Create collections.

        Args:
            descriptions: List of collections descriptions, each
                description is a dictionary with keys among arguments
                of ``create()``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            List of resource for the created collections.

        """
        data = kwargs
        data['collections'] = descriptions
        descs = self._provider.post('create-collections', data=data)
        return [Resource(**desc)
                for desc in descs]

    def describe(self, collection: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a collection or a list of collections.

        Args:
            collection: Identifier of the collection to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The fature description or a list of collection description.

        """
        data = kwargs
        if isinstance(collection, list):
            data['collections'] = collection
            descs = self._provider.post('describe-collections',
                                        data=data)
            return [Resource(**desc)
                    for desc in descs]
        else:
            data['collection'] = collection
            desc = self._provider.post('describe-collection', data=data)
            return Resource(**desc)

    def delete(self, collection: SomeResourceIds, *, permanent: bool = False,
               **kwargs):
        """Delete a collection or multiple collections.

        Args:
            collection: Identifier of the collection to delete, or list of
                such identifiers.

            permanent: Whether to delete collections permanently or not.
                Default to False.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if isinstance(collection, list):
            path = 'delete-collections' if not permanent \
                else 'delete-collections-permanently'
            data['collections'] = collection
        else:
            path = 'delete-collection' if not permanent \
                else 'delete-collection-permanently'
            data['collection'] = collection

        self._provider.post(path=path, data=data, as_json=False)

    def restore(self, collection: SomeResourceIds, **kwargs):
        """Restore a collection or multiple collections.

        Args:
            collection: Identifier of the collection to restore, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if isinstance(collection, list):
            path = 'restore-collections'
            data['collections'] = collection
        else:
            path = 'restore-collection'
            data['collection'] = collection

        self._provider.post(path=path, data=data, as_json=True)

    def export(self,
               collection: ResourceId,
               target_path: str,
               target_name: str,
               format_requested: str = 'geojson'):
        """Export a collection to the given format.

        Args:
            collection: Identifier of the collection.

            target_path: Path where the file will be download.

            target_name: Name given to the downloaded file.

            format_requested: Format of the export.

        Return:
            File path of the download file.

        """
        if target_path is None:
            target_path = '.'

        path = 'export-collection'
        params = {'collection': collection, 'format': format_requested}
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        resp = self._provider.post(path, as_json=False,
                                   data=params)
        file_path = os.path.join(target_path, target_name)
        with open(file_path, 'wb') as fh:
            fh.write(resp)

        return file_path
