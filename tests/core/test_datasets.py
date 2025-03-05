"""Test utilities related to SRS."""

from unittest import TestCase

from alteia.apis.client.datamngt.datasetsimpl import _adapt_params


class TestDatasets(TestCase):
    """Test Datasets related functions."""

    def test_adapt_parameters(self):
        """Test adaptation of parameters when creating a dataset."""
        assert _adapt_params(
            {
                "name": "dataset name",
                "type": "vector",
                "source_name": "data-manager",
                "dataset_format": "geojson",
                "company": "company-id",
                "mission": None,  # Will be removed
                "vertical_srs_wkt": None,  # Will be removed
                "other_prop": None,  # Will be kept since it is not a common param
            }
        ) == {
            "name": "dataset name",
            "type": "vector",
            "source": {"name": "data-manager"},
            "format": "geojson",
            "company": "company-id",
            "other_prop": None,
        }
