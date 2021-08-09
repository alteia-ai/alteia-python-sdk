from pkgutil import extend_path

from alteia.sdk import SDK

__all__ = ('SDK',)

__version__ = '1.3.1'  # must match the version in pyproject.toml

__path__ = extend_path(__path__, __name__)
