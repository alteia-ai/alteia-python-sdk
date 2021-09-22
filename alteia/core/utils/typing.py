"""Definitions related to type hints.

"""
import pathlib
from typing import List, Tuple, Union

from alteia.core.resources.resource import Resource

AnyPath = Union[str, pathlib.Path]

ResourceId = str

SomeResourceIds = Union[ResourceId, List[ResourceId]]

SomeResources = Union[Resource, List[Resource]]

Offset = Tuple[float, float, float]
