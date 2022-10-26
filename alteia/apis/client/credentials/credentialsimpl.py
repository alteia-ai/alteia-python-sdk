"""
    Credential implementation
"""

from typing import Any, Dict, List, Union

from alteia.apis.provider import CredentialsServiceAPI
from alteia.core.errors import ParameterError
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.utils.typing import Resource, ResourceId

DOCKER = 'docker'
OBJECT_STORAGE = 'object-storage'


class CredentialsImpl:
    def __init__(self,
                 credentials_service_api: CredentialsServiceAPI,
                 **kwargs):
        self._provider = credentials_service_api

    def search(self, *, name: Union[str, List[str]] = None, filter: Dict = None,
               limit: int = None, page: int = None, sort: dict = None,
               return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search for a list of credentials.

        Args:
            name: Credential name, should be a string or list of string.

            filter: Search filter dictionary (refer to ``/search-credentials``
                definition in the Credentials Service API for a detailed
                description of ``filter``).

            limit: Optional Maximum number of results to extract.

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
            Credentials: A list of credential resources OR a namedtuple
                with total number of results and list of credential resources.

        """
        data = kwargs

        for prop_name, value in [('filter', filter or {}),
                                 ('limit', limit),
                                 ('page', page),
                                 ('sort', sort)]:
            if value is not None:
                data.update({prop_name: value})

        if name is not None:
            name_value: Dict[str, Any]
            if isinstance(name, list):
                name_value = {'$in': name}
            else:
                name_value = {'$eq': name}
            data['filter']['name'] = name_value

        search_desc = self._provider.post(
            path='search-credentials', data=data, as_json=True)

        credentials = search_desc.get('results')

        results = [Resource(**credential) for credential in credentials]

        if return_total:
            total = search_desc.get('total')
            return ResourcesWithTotal(total=total, results=results)

        return results

    def create(self, *, name: str, credentials_type: str = DOCKER, credentials: Dict[str, str],
               **kwargs) -> Resource:
        """Create a credential entry.

        Args:
            name: Credential name (must be unique).

            credentials_type : Credentials type (docker or object-storage), default: docker

            credentials: Credential dict.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created credential description.

        Examples:
            >>> sdk.credentials.create(name="My Docker registry",
            ...     credentials={
            ...         "type": "docker",
            ...         "login": "my_login",
            ...         "password": "my_password",
            ...         "registry": "mydockerregistry.com"
            ...     }
            ... )
            Resource(_id='5e5155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(name="My Docker registry",
            ...     credentials={
            ...         "type": "aws",
            ...         "aws_access_key_id": "key_id",
            ...         "aws_secret_access_key": "password_test",
            ...         "aws_region": "us-east-1",
            ...         "registry": "XXX..dkr.ecr.us-east-1.amazonaws.com"
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(name="My bucket S3",
            ...     credentials={
            ...         "type": "s3",
            ...         "aws_access_key_id": "key_id",
            ...         "aws_secret_access_key": "password_test",
            ...         "aws_region": "us-east-1",
            ...         "registry": "XXX..s3.us-east-1.amazonaws.com/key"
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

        """
        data = kwargs

        if credentials_type not in [DOCKER, OBJECT_STORAGE]:
            raise ParameterError('Type of credentials is wrong')

        data.update({
            'name': name,
            'type': credentials_type,
            'credentials': credentials
        })

        desc = self._provider.post(
            path='create-credentials', data=dict(data), as_json=True)

        return Resource(**desc)

    def delete(self, credential: ResourceId, **kwargs) -> None:
        """Delete a credential entry.

        Args:
            credential: Credential identifier.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'credentials':  credential})

        self._provider.post(
            path='delete-credentials',
            data=data,
            as_json=False
        )
