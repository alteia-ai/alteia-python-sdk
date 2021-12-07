from typing import List, Optional

from semantic_version import NpmSpec, Version


def select_version(versions: List[Version], *,
                   spec: NpmSpec = None) -> Optional[Version]:
    """Select a version according to given specification.

    Args:
        versions: List of versions to parse.

        spec: A version specification.

    Returns:
       The selected version according to ``spec`` or highest version
       if ``spec`` is ``None``.

    """
    if len(versions) == 0:
        return None

    if spec is not None:
        selected_version = spec.select(versions)
    else:
        versions.sort()
        selected_version = versions[-1]

    return selected_version
