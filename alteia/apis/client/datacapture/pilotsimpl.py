from alteia.apis.provider import AssetManagementAPI
from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import SomeResourceIds, SomeResources
from alteia.core.utils.utils import get_chunks


class PilotsImpl:
    def __init__(self, asset_management_api: AssetManagementAPI, **kwargs):
        self._provider = asset_management_api

    def describe(self, pilot: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a pilot or list of pilots.

                Args:
                    pilot: Identifier of the pilot to describe, or list of
                        such identifiers.

                    **kwargs: Optional keyword arguments. Those arguments are
                        passed as is to the API provider.

                Returns:
                    Resource: A pilot resource or a list of pilot resources.

                """
        data = kwargs
        if isinstance(pilot, list):
            results = []
            ids_chunks = get_chunks(pilot, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data['pilots'] = ids_chunk
                descs = self._provider.post('describe-pilots', data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data['pilot'] = pilot
            desc = self._provider.post('describe-pilot', data=data)
            return Resource(**desc)
