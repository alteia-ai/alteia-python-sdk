import json

from alteia.core.connection.connection import Connection
from alteia.core.utils.utils import sanitize_dict


class Provider(object):
    _root_path = ''

    def __init__(self, connection: Connection):
        self._connection = connection

    def get(self, path, *, preload_content=True, as_json=True):
        headers = {'Cache-Control': 'no-cache'}
        full_path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.get(path=full_path,
                                       headers=headers,
                                       as_json=as_json,
                                       preload_content=preload_content)

        return content

    def post(self, path, data, *, sanitize=False, serialize=True,
             preload_content=True, as_json=True):
        """Post the given data.

        Args:
            path: Relative URL.

            data: The data to send.

            sanitize: Whether to recursively remove special characters
                from data keys.

            serialize: Whether to serialize ``data`` to JSON.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

        Returns:
            Response body eventually deserialized.

        """
        if sanitize:
            data = sanitize_dict(data)

        if serialize:
            data = json.dumps(data)
            content_type = 'application/json'
        else:
            content_type = 'application/octet-stream'

        headers = {'Cache-Control': 'no-cache'}
        headers['Content-Type'] = content_type
        full_path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.post(path=full_path,
                                        headers=headers,
                                        data=data,
                                        as_json=as_json,
                                        preload_content=preload_content)
        return content

    def put(self, path, data, *, sanitize=True, serialize=True,
            preload_content=True, as_json=True):
        """Put the given data.

        Args:
            path: Relative URL.

            data: The data to send.

            sanitize: Whether to recursively remove special characters
                from data keys.

            serialize: Whether to serialize ``data`` to JSON.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

        Returns:
            Response body eventually deserialized.

        """
        if sanitize:
            data = sanitize_dict(data)

        if serialize:
            data = json.dumps(data)
            content_type = 'application/json'
        else:
            content_type = 'application/octet-stream'

        headers = {'Cache-Control': 'no-cache'}
        headers['Content-Type'] = content_type
        path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.put(path=path,
                                       headers=headers,
                                       data=data,
                                       as_json=as_json,
                                       preload_content=preload_content)
        return content

    def delete(self, path, *, preload_content=True, as_json=True):
        """Delete.

        Args:
            path: Relative URL.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

        Returns:
            Response body eventually deserialized.

        """
        headers = {'Cache-Control': 'no-cache',
                   'Content-Type': 'application/json'}
        path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.delete(path=path,
                                          headers=headers,
                                          preload_content=preload_content,
                                          as_json=True)
        return content


class WithSearchRoute():
    _search_path = 'search'

    def search(self, path, query):
        """Search objects.

        """
        content = self._connection.post(
                path='{root_path}/{path}/{search_path}'.format(root_path=self._root_path,
                                                               path=path,
                                                               search_path=self._search_path),
                headers={'Cache-Control': 'no-cache', 'Content-Type': 'application/json'},
                data=json.dumps(query),
                as_json=True)

        return content


class AnnotationsAPI(Provider):
    _root_path = 'map-service/annotations'


class AuthAPI(WithSearchRoute, Provider):
    _root_path = 'dxauth'


class ProjectManagerAPI(WithSearchRoute, Provider):
    _root_path = 'dxpm'


class DataManagementAPI(Provider):
    _root_path = 'data-manager'


class UIServicesAPI(Provider):
    _root_path = 'uisrv'


class AnalyticsServiceAPI(Provider):
    _root_path = 'analytics-service'


class ExternalProviderServiceAPI(Provider):
    _root_path = 'external-providers-service'


class AssetManagementAPI(Provider):
    _root_path = 'dct-service/asset-management'


class CollectionTaskAPI(Provider):
    _root_path = 'dct-service/task'


class CollectionTaskManagementAPI(Provider):
    _root_path = 'dct-service/task-management'
