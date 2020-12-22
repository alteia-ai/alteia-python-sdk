from typing import List

from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId, SomeResourceIds, SomeResources


class CarriersImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def create(self, *, carrier_model: str, team: ResourceId, serial_number: str,
               firmware: str = None, status: str = None, comment: str = None,
               **kwargs) -> Resource:
        """Create a carrier.

        Args:
            carrier_model: Identifier of the carrier model.

            team: Identifier of the team.

            serial_number: Serial number of the carrier.

            firmware : Optional firmware.

            status: Optional status,
                among ``ready``, ``in-maintenance``, ``out-of-service``.

            comment: Optional comment.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A carrier resource.
        """
        data = kwargs
        data.update({
            'carrier_model': carrier_model,
            'team': team,
            'serial_number': serial_number
        })

        for param_name, param_value in (('status', status),
                                        ('comment', comment),
                                        ('firmware', firmware)):
            if param_value is not None:
                data[param_name] = param_value

        content = self._provider.post(path='create-carrier', data=data)

        return Resource(**content)

    def search(self, *, filter: dict = None, limit: int = None,
               page: int = None, sort: dict = None, **kwargs
               ) -> List[Resource]:
        """Search carriers.

        Args:
            filter: Search filter dictionary.

            limit: Maximum number of results to extract.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resources: A list of carrier resources.

        """

        data = kwargs

        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post('search-carriers', data=data)
        results = r.get('results')

        return [Resource(**m) for m in results]

    def describe(self, carrier: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a carrier or a list of carriers.

        Args:
            carrier: Identifier of the carrier to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The carrier description or a list of carriers descriptions.

        """
        data = kwargs
        if isinstance(carrier, list):
            data['carriers'] = carrier
            descs = self._provider.post('describe-carriers', data=data)
            return [Resource(**desc) for desc in descs]
        else:
            data['carrier'] = carrier
            desc = self._provider.post('describe-carrier', data=data)
            return Resource(**desc)

    def delete(self, carrier: ResourceId, **kwargs):
        """Delete a carrier.

        Args:
            carrier: Identifier of the carrier to delete.

        """

        data = kwargs
        data['carrier'] = carrier

        self._provider.post('delete-carrier', data=data)
