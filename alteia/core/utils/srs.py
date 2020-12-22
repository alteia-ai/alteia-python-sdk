from typing import AnyStr

from pkg_resources import resource_string


def __name2wkt(name: AnyStr, *, wkts_path: AnyStr) -> AnyStr:
    """Convert a vert SRS name to WKT format.

    Args:
        name: Name of vertical SRS to convert.

        wkts_path: Path to the WKTs directory.

    Raises:
        ValueError: When ``name`` doesn't match any known WKT file.

    """
    name = name.lower()
    res_name = '{}/{}.wkt'.format(wkts_path, name)
    try:
        wkt = resource_string(__name__, res_name).decode('utf-8')
        flatten_wkt = ''.join([line.strip() for line in wkt.splitlines()])
        return flatten_wkt
    except FileNotFoundError:
        raise ValueError('Unknown SRS name: {}'.format(name))


def expand_vertcrs_to_wkt(desc: AnyStr) -> AnyStr:
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
        return __name2wkt(desc, wkts_path='vertcrs')
    except ValueError:
        pass
    return desc
