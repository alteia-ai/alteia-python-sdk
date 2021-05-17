import json

from alteia.core.connection.connection import Connection
from alteia.core.utils.utils import sanitize_dict

DEFAULT_API_TIMEOUT = 30.0  # value in seconds


class Provider(object):
    _root_path = ''
    api_timeout = DEFAULT_API_TIMEOUT

    def __init__(self, connection: Connection):
        self._connection = connection

    def get(self, path, *, preload_content=True, as_json=True, timeout=None):
        headers = {'Cache-Control': 'no-cache'}
        full_path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.get(path=full_path,
                                       headers=headers,
                                       timeout=timeout or self.api_timeout,
                                       as_json=as_json,
                                       preload_content=preload_content)

        return content

    def post(self, path, data, *, sanitize=False, serialize=True,
             preload_content=True, as_json=True, timeout=None):
        """Post the given data.

        Args:
            path: Relative URL.

            data: The data to send.

            sanitize: Whether to recursively remove special characters
                from data keys.

            serialize: Whether to serialize ``data`` to JSON.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

            timeout: Timeout in seconds for API call

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
                                        timeout=timeout or self.api_timeout,
                                        as_json=as_json,
                                        preload_content=preload_content)
        return content

    def put(self, path, data, *, sanitize=True, serialize=True,
            preload_content=True, as_json=True, timeout=None):
        """Put the given data.

        Args:
            path: Relative URL.

            data: The data to send.

            sanitize: Whether to recursively remove special characters
                from data keys.

            serialize: Whether to serialize ``data`` to JSON.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

            timeout: Timeout in seconds for API call

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
                                       timeout=timeout or self.api_timeout,
                                       as_json=as_json,
                                       preload_content=preload_content)
        return content

    def delete(self, path, *, preload_content=True, as_json=True, timeout=None):
        """Delete.

        Args:
            path: Relative URL.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

            timeout: Timeout in seconds for API call

        Returns:
            Response body eventually deserialized.

        """
        headers = {'Cache-Control': 'no-cache',
                   'Content-Type': 'application/json'}
        path = '{root}/{path}'.format(root=self._root_path, path=path)
        content = self._connection.delete(path=path,
                                          headers=headers,
                                          timeout=timeout or self.api_timeout,
                                          preload_content=preload_content,
                                          as_json=True)
        return content


class WithSearchRoute():
    _search_path = 'search'
    timeout = DEFAULT_API_TIMEOUT

    def search(self, path, query):
        """Search objects.

        """
        content = self._connection.post(
                path='{root_path}/{path}/{search_path}'.format(root_path=self._root_path,
                                                               path=path,
                                                               search_path=self._search_path),
                headers={'Cache-Control': 'no-cache', 'Content-Type': 'application/json'},
                data=json.dumps(query),
                timeout=self.timeout,
                as_json=True)

        return content


class AnnotationsAPI(Provider):
    _root_path = 'map-service/annotations'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class AuthAPI(WithSearchRoute, Provider):
    _root_path = 'dxauth'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class ProjectManagerAPI(WithSearchRoute, Provider):
    _root_path = 'dxpm'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class DataManagementAPI(Provider):
    _root_path = 'data-manager'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class UIServicesAPI(Provider):
    _root_path = 'uisrv'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class AnalyticsServiceAPI(Provider):
    _root_path = 'analytics-service'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class ExternalProviderServiceAPI(Provider):
    _root_path = 'external-providers-service'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class AssetManagementAPI(Provider):
    _root_path = 'dct-service/asset-management'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class CollectionTaskAPI(Provider):
    _root_path = 'dct-service/task'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service


class CollectionTaskManagementAPI(Provider):
    _root_path = 'dct-service/task-management'
    api_timeout = DEFAULT_API_TIMEOUT  # todo: define from service
