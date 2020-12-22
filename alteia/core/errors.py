"""Package errors.

"""

__all__ = ('ConfigError', 'FileError', 'ImmutableAttribute',
           'MissingCredentialsError', 'QueryError', 'ResponseError',
           'TokenRenewalError', 'UnsupportedOperationError',
           'UnsupportedResourceError', 'UploadError',
           'DownloadError', 'BoundingBoxError', 'ParameterError', 'SearchError')


class _Error(Exception):
    """Base class for all package exceptions.

    """
    def __init__(self, msg=''):
        super().__init__(msg)


class ConfigError(_Error):
    pass


class FileError(_Error):
    pass


class ImmutableAttribute(_Error):
    _msg = 'The attribute {} is immutable'

    def __init__(self, name):
        super().__init__(self._msg.format(name))


class UnsupportedOperationError(_Error):
    def __init__(self):
        super().__init__('The operation is not supported')


class UnsupportedResourceError(_Error):
    _msg = 'Resource {} is not supported'

    def __init__(self, resource_name):
        super().__init__(self._msg.format(resource_name))


class QueryError(_Error):
    pass


class ResponseError(_Error):
    pass


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
