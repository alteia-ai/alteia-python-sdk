try:
    import importlib.resources as pkg_resources
except ImportError:
    # Python < 3.7 uses `importlib_resources`.
    import importlib_resources as pkg_resources

from alteia.core.utils import vertcrs


def read_text_from_resource(package: str, resource: str) -> str:
    try:
        content = pkg_resources.files(package).joinpath(resource).read_text()
        return content
    except AttributeError:
        # Python < 3.9
        return pkg_resources.read_text(package, resource)


def __name2wkt(name: str) -> str:
    """Convert a vert SRS name to WKT format.

    Args:
        name: Name of vertical SRS to convert.

    Raises:
        ValueError: When ``name`` doesn't match any known WKT file.

    """
    name = name.lower()
    res_name = f'{name}.wkt'
    try:
        wkt = read_text_from_resource(vertcrs.__name__, res_name)
        flatten_wkt = ''.join([line.strip() for line in wkt.splitlines()])
        return flatten_wkt
    except FileNotFoundError:
        raise ValueError(f'Unknown SRS name: {name}')


def expand_vertcrs_to_wkt(desc: str) -> str:
    """Expand a vertical SRS description to WKT format.

    The supported SRS names are ``"arbitrary"``, ``"arbitrary_feet"``,
    ``"arbitrary_feet_us"``, ``"egm96"``, ``"egm96_feet"``,
    ``"egm96_feet_us"``, ``"egm2008"``, ``"egm2008_feet"``,
    ``"egm2008_feet_us"``, ``"wgs84"``, ``"wgs84_feet"`` or
    ``"wgs84_feet_us"``.

    Args:
        desc: A WKT or one of the supported SRS names.

    Returns:
        If ``desc`` is equal to one of the supported SRS names, the
        corresponding WKT is returned. Otherwise ``desc`` is returned.

    """
    try:
        return __name2wkt(desc)
    except ValueError:
        pass
    return desc
