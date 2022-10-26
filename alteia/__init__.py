from pkgutil import extend_path
from typing import Iterable

from alteia.sdk import SDK

__all__ = ('SDK',)

__version__ = '2.5.1'  # must match the version in pyproject.toml

__path__: Iterable[str] = extend_path(__path__, __name__)  # type: ignore # noqa
