"""Package errors."""

import json
from typing import Any

__all__ = (
    "ConfigError",
    "FileError",
    "ImmutableAttribute",
    "MissingCredentialsError",
    "QueryError",
    "ResponseError",
    "TokenRenewalError",
    "UnsupportedOperationError",
    "UnsupportedResourceError",
    "UploadError",
    "DownloadError",
    "BoundingBoxError",
    "ParameterError",
    "SearchError",
)


class _Error(Exception):
    """Base class for all package exceptions."""

    def __init__(self, msg=""):
        super().__init__(msg)


class ConfigError(_Error):
    pass


class FileError(_Error):
    pass


class ImmutableAttribute(_Error):
    _msg = "The attribute {} is immutable"

    def __init__(self, name):
        super().__init__(self._msg.format(name))


class UnsupportedOperationError(_Error):
    def __init__(self):
        super().__init__("The operation is not supported")


class UnsupportedResourceError(_Error):
    _msg = "Resource {} is not supported"

    def __init__(self, resource_name):
        super().__init__(self._msg.format(resource_name))


class QueryError(_Error):
    pass


class ResponseError(_Error):
    def __init__(self, msg, status: int = 0, data=None):
        super(ResponseError, self).__init__(msg=msg)
        self.status: int = status
        self.data: Any | None = None

        # information from data
        self.service: str | None = None
        self.code: str | None = None  # not the HTTP code but the service error code name
        self.message: str | None = None
        self.details: Any | None = None
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        try:
            self.data = json.loads(data)
            if isinstance(self.data, dict):
                self.service = self.data.get("service")
                self.code = self.data.get("code")
                self.message = self.data.get("message")
                self.details = self.data.get("details")
        except Exception:
            # the response content is not json-like (could be a simple text response)
            self.data = data


class MissingCredentialsError(_Error):
    pass


class TokenRenewalError(_Error):
    pass


class UploadError(_Error):
    pass


class DownloadError(_Error):
    pass


class BoundingBoxError(_Error):
    pass


class ParameterError(_Error):
    pass


class SearchError(_Error):
    pass
