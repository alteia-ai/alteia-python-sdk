"""
Credential implementation
"""

import logging
from typing import Any, Dict, List, Mapping, Union

from alteia.apis.provider import CredentialsServiceAPI
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.utils.typing import Resource, ResourceId

LOGGER = logging.getLogger(__name__)

DOCKER = "docker"
OBJECT_STORAGE = "object-storage"
STAC_CATALOG = "stac-catalog"

OBJECT_STORAGE_TYPES = ("s3", "azure-blob", "google-cloud-storage")
DOCKER_TYPES = ("aws", "docker")
STAC_CATALOG_TYPES = "oauth"


class CredentialsImpl:
    def __init__(self, credentials_service_api: CredentialsServiceAPI, **kwargs):
        self._provider = credentials_service_api

    def search(
        self,
        *,
        name: Union[str, List[str]] | None = None,
        filter: Dict | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort: dict | None = None,
        return_total: bool = False,
        **kwargs,
    ) -> Union[ResourcesWithTotal, List[Resource]]:
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

        for prop_name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
        ]:
            if value is not None:
                data.update({prop_name: value})

        if name is not None:
            name_value: Dict[str, Any]
            if isinstance(name, list):
                name_value = {"$in": name}
            else:
                name_value = {"$eq": name}
            data["filter"]["name"] = name_value

        search_desc = self._provider.post(path="search-credentials", data=data, as_json=True)

        credentials = search_desc.get("results")

        results = [Resource(**credential) for credential in credentials]

        if return_total:
            total = search_desc.get("total")
            return ResourcesWithTotal(total=total, results=results)

        return results

    def create(
        self,
        *,
        name: str,
        company: str,
        credentials: Dict[str, Any],
        labels: Mapping[str, str] | None = None,
        **kwargs,
    ) -> Resource:
        """Create a credential entry.

        Args:
            name: Credential name (must be unique).

            company: Company ID.

            credentials: Credential dict.

            labels: Labels mapping.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created credential description.

        Examples:
            >>> sdk.credentials.create(
            ...     name="My Docker registry",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "docker",
            ...         "login": "my_login",
            ...         "password": "my_password",
            ...         "registry": "mydockerregistry.com"
            ...     },
            ...     labels={
            ...         "type": "docker",
            ...         "registry": "mydockerregistry.com"
            ...     }
            ... )
            Resource(_id='5e5155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(
            ...     name="My aws registry",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "aws",
            ...         "aws_access_key_id": "key_id",
            ...         "aws_secret_access_key": "password_test",
            ...         "aws_region": "us-east-1",
            ...     },
            ...     labels={
            ...         "type": "docker",
            ...         "registry": "XXX.dkr.ecr.us-east-1.amazonaws.com"
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(
            ...     name="My bucket S3",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "s3",
            ...         "aws_access_key_id": "key_id",
            ...         "aws_secret_access_key": "password_test",
            ...         "aws_region": "us-east-1",
            ...     },
            ...     labels={
            ...         "type": "object-storage",
            ...         "bucket": "XXX.s3.us-east-1.amazonaws.com/key"
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(
            ...     name="My azure blob",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "azure-blob",
            ...         "azure_client_id": "key_id",
            ...         "azure_tenant_id": "tenant-id",
            ...         "azure_client_secret": "client_secret",
            ...     },
            ...     labels={
            ...         "type": "object-storage",
            ...         "bucket": "XXX.s3.us-east-1.amazonaws.com/key",
            ...         "account_url": "https://mystorage.blob.core.windows.net"
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

            >>> sdk.credentials.create(
            ...     name="My stac catalog",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "oauth",
            ...         "client_id": "key_id",
            ...         "client_secret": "client_secret",
            ...         "token_url": "https://token_url",
            ...     },
            ...     labels={
            ...         "type": "stac-catalog",
            ...         "catalog": "https://catalog_url",
            ...     }
            ... )
            Resource(_id='5e6155ae8dcb064fcbf4ae35')

        """
        data = kwargs

        data.update({"name": name, "company": company, "credentials": credentials})
        if labels:
            data.update({"labels": labels})

        desc = self._provider.post(path="create-credentials", data=dict(data), as_json=True)

        return Resource(**desc)

    def delete(self, credential: ResourceId, **kwargs) -> None:
        """Delete a credential entry.

        Args:
            credential: Credential identifier.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"credentials": credential})

        self._provider.post(path="delete-credentials", data=data, as_json=False)

    def set_credentials(self, company: str, name: str, credentials: Dict[str, Any], **kwargs) -> Resource:
        """Set a credential entry.

        Args:
            company: Company ID.

            name: Credentials name.

            credentials: Credential dict.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            An empty json object.

        Examples:
            >>> sdk.credentials.set_credentials(
            ...     name="My Docker registry",
            ...     company="507f191e810c19729de860eb",
            ...     credentials={
            ...         "type": "docker",
            ...         "login": "my_login",
            ...         "password": "my_password",
            ...         "registry": "mydockerregistry.com"
            ...     }
            ... )
        """
        data = kwargs
        data.update({"company": company, "name": name, "credentials": credentials})
        desc = self._provider.post(path="set-credentials", data=dict(data), as_json=True)

        return Resource(**desc)

    def set_labels(self, company: str, name: str, labels: Mapping[str, str], **kwargs) -> Resource:
        """Set labels.

        Args:
            company: Company ID.

            name: Credentials name.

            labels: Labels mapping of string/string.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            An empty json object.

        Examples:
            >>> sdk.credentials.set_labels(
            ...     name="up-42",
            ...     company="507f191e810c19729de860eb",
            ...     labels={
            ...         "type": "stac-catalog",
            ...         "catalog": "https://api.up42.com/v2/assets/stac",
            ...     }
            ... )
        """
        data = kwargs
        data.update({"company": company, "name": name, "labels": labels})
        desc = self._provider.post(path="set-labels", data=dict(data), as_json=True)

        return Resource(**desc)
