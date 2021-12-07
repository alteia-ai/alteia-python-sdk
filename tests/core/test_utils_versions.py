"""Test utilities related to versions.

"""

from unittest import TestCase

from semantic_version import NpmSpec, Version

from alteia.core.utils.versions import select_version


class VersionsUtils(TestCase):
    """Test versios related utilities.

    """
    def test_select_version_without_spec(self):
        versions = [Version('0.0.3'), Version('1.1.1'), Version('1.1.2')]
        version = select_version(versions)
        self.assertEqual(version, Version('1.1.2'))

    def test_select_version_with_spec(self):
        versions = [Version('0.0.3'), Version('1.1.1'), Version('1.1.2')]
        version = select_version(versions, spec=NpmSpec('0.0.x'))
        self.assertEqual(version, Version('0.0.3'))

    def test_select_version_with_empty_candidates(self):
        versions = []
        version = select_version(versions)
        self.assertIsNone(version)

        version = select_version(versions, spec=NpmSpec('0.0.x'))
        self.assertIsNone(version)
