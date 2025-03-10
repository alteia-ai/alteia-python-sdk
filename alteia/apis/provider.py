import json
from typing import Any, Dict, Optional

from alteia.core.connection.connection import Connection
from alteia.core.utils.utils import sanitize_dict

DEFAULT_API_TIMEOUT = 600.0  # value in seconds
DEFAULT_MAX_ELEMENTS_PER_DESCRIBE_REQUEST = 1000
DEFAULT_MAX_ELEMENTS_PER_DELETE_REQUEST = 100


class Provider:
    _root_path = ""
    api_timeout = DEFAULT_API_TIMEOUT
    max_per_describe = DEFAULT_MAX_ELEMENTS_PER_DESCRIBE_REQUEST
    max_per_delete = DEFAULT_MAX_ELEMENTS_PER_DELETE_REQUEST

    def __init__(self, connection: Connection):
        self._connection = connection

    def get(
        self,
        path,
        *,
        preload_content=True,
        as_json=True,
        timeout=None,
        headers: Optional[Dict[str, Any]] | None = None,
    ):
        request_headers = {"Cache-Control": "no-cache"}
        if headers:
            request_headers.update(headers)

        full_path = f"{self._root_path}/{path}"
        content = self._connection.get(
            path=full_path,
            headers=request_headers,
            timeout=timeout or self.api_timeout,
            as_json=as_json,
            preload_content=preload_content,
        )

        return content

    def post(
        self,
        path,
        data,
        *,
        sanitize=False,
        serialize=True,
        preload_content=True,
        as_json=True,
        timeout=None,
        headers: Optional[Dict[str, Any]] | None = None,
    ):
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

            headers: Headers in dict format

        Returns:
            Response body eventually deserialized.

        """
        if sanitize:
            data = sanitize_dict(data)

        if serialize:
            data = json.dumps(data)
            content_type = "application/json"
        else:
            content_type = "application/octet-stream"

        request_headers = {"Cache-Control": "no-cache", "Content-Type": content_type}
        if headers:
            request_headers.update(headers)

        full_path = f"{self._root_path}/{path}"
        content = self._connection.post(
            path=full_path,
            headers=request_headers,
            data=data,
            timeout=timeout or self.api_timeout,
            as_json=as_json,
            preload_content=preload_content,
        )
        return content

    def put(
        self,
        path,
        data,
        *,
        sanitize=True,
        serialize=True,
        preload_content=True,
        as_json=True,
        timeout=None,
        headers: Optional[Dict[str, Any]] | None = None,
    ):
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

            headers: Headers in dict format

        Returns:
            Response body eventually deserialized.

        """
        if sanitize:
            data = sanitize_dict(data)

        if serialize:
            data = json.dumps(data)
            content_type = "application/json"
        else:
            content_type = "application/octet-stream"

        request_headers = {"Cache-Control": "no-cache", "Content-Type": content_type}
        if headers:
            request_headers.update(headers)

        path = f"{self._root_path}/{path}"
        content = self._connection.put(
            path=path,
            headers=request_headers,
            data=data,
            timeout=timeout or self.api_timeout,
            as_json=as_json,
            preload_content=preload_content,
        )
        return content

    def delete(
        self,
        path,
        *,
        preload_content=True,
        as_json=True,
        timeout=None,
        headers: Optional[Dict[str, Any]] | None = None,
    ):
        """Delete.

        Args:
            path: Relative URL.

            preload_content: Whether to preload the response content.

            as_json: Whether to deserialize the response body from JSON.

            timeout: Timeout in seconds for API call

            headers: Headers in dict format

        Returns:
            Response body eventually deserialized.

        """
        request_headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)

        path = f"{self._root_path}/{path}"
        content = self._connection.delete(
            path=path,
            headers=request_headers,
            timeout=timeout or self.api_timeout,
            preload_content=preload_content,
            as_json=as_json,
        )
        return content


class WithSearchRoute:
    _search_path = "search"
    timeout = DEFAULT_API_TIMEOUT

    def search(self, path, query):
        """Search objects."""
        content = self._connection.post(
            path=f"{self._root_path}/{path}/{self._search_path}",
            headers={"Cache-Control": "no-cache", "Content-Type": "application/json"},
            data=json.dumps(query),
            timeout=self.timeout,
            as_json=True,
        )

        return content


class FeaturesServiceAPI(Provider):
    _root_path = "map-service/features"


class AnnotationsAPI(Provider):
    _root_path = "map-service/annotations"
    api_timeout = DEFAULT_API_TIMEOUT


class AuthAPI(WithSearchRoute, Provider):
    _root_path = "dxauth"
    api_timeout = DEFAULT_API_TIMEOUT


class DataManagementAPI(Provider):
    _root_path = "data-manager"
    api_timeout = DEFAULT_API_TIMEOUT


class ProjectManagerAPI(Provider):
    _root_path = "project-manager"  # alias of uisrv
    api_timeout = DEFAULT_API_TIMEOUT


class AnalyticsServiceAPI(Provider):
    _root_path = "analytics-service"
    api_timeout = DEFAULT_API_TIMEOUT


class CredentialsServiceAPI(Provider):
    _root_path = "credentials-service"
    api_timeout = DEFAULT_API_TIMEOUT


class AssetManagementAPI(Provider):
    _root_path = "dct-service/asset-management"
    api_timeout = DEFAULT_API_TIMEOUT


class CollectionTaskAPI(Provider):
    _root_path = "dct-service/task"
    api_timeout = DEFAULT_API_TIMEOUT


class CollectionTaskManagementAPI(Provider):
    _root_path = "dct-service/task-management"
    api_timeout = DEFAULT_API_TIMEOUT


class DataflowServiceAPI(Provider):
    _root_path = "dataflow"
    api_timeout = DEFAULT_API_TIMEOUT


class SeasonPlannerAssetManagementAPI(Provider):
    _root_path = "season-planner/asset-management"
    api_timeout = DEFAULT_API_TIMEOUT


class SeasonPlannerTrialManagementAPI(Provider):
    _root_path = "season-planner/trial-management"
    api_timeout = DEFAULT_API_TIMEOUT


class SeasonPlannerAPI(Provider):
    _root_path = "season-planner"
    api_timeout = DEFAULT_API_TIMEOUT
