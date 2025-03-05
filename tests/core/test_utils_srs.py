"""Test utilities related to SRS."""

from unittest import TestCase

from alteia.core.utils.srs import expand_vertcrs_to_wkt

WGS84_WKT = """
VERT_CS["WGS84 ellipsoid (meters)",
  VERT_DATUM["Ellipsoid",2002],
    UNIT["metre",1,
      AUTHORITY["EPSG","9001"]],
    AXIS["Up",UP]]
"""

EGM96_WKT = """
VERT_CS["EGM96 geoid (meters)",
  VERT_DATUM["EGM96 geoid",2005,
    EXTENSION["PROJ4_GRIDS","egm96_15.gtx"],
    AUTHORITY["EPSG","5171"]],
  UNIT["metre",1,
    AUTHORITY["EPSG","9001"]],
  AXIS["Up",UP]]
"""

ARBITRARY_WKT = """
VERT_CS["Arbitrary",
    VERT_DATUM["Arbitrary",2000],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Up",UP]]
"""


def _clean_whitespaces(a):
    return a.replace("\n", "").replace(" ", "").replace("\r", "")


class SRSUtilsTest(TestCase):
    """Test SRS related utilities."""

    def test_expand_vertcrs_to_wkt(self):
        """Test conversion of SRS names."""
        self.assertEqualSkipSpaces(expand_vertcrs_to_wkt("wgs84"), WGS84_WKT)
        self.assertEqualSkipSpaces(expand_vertcrs_to_wkt("egm96"), EGM96_WKT)
        self.assertEqualSkipSpaces(expand_vertcrs_to_wkt("arbitrary"), ARBITRARY_WKT)
        self.assertEqual(expand_vertcrs_to_wkt("fake"), "fake")

    def assertEqualSkipSpaces(self, first, second, msg=None):
        """Test that first and second are equal after whitespaces removal."""
        return self.assertEqual(_clean_whitespaces(first), _clean_whitespaces(second), msg)
