"""Definitions related to type hints.

"""
import pathlib
from typing import List, NewType, Tuple, Union

from alteia.core.resources.resource import Resource

AnyPath = NewType('AnyPath', Union[str, pathlib.Path])

ResourceId = NewType('ResourceId', str)


SomeResourceIds = NewType('SomeResourceIds',
                          Union[ResourceId, List[ResourceId]])

SomeResources = NewType('SomeResources',
                        Union[Resource, List[Resource]])

Offset = NewType('Offset', Tuple[float, float, float])
