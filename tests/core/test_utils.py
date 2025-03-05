import copy
import datetime

from alteia.core.config import ConnectionConfig
from alteia.core.errors import ConfigError
from alteia.core.utils.utils import (
    dict_merge,
    find,
    flatten_dict,
    get_chunks,
    new_instance,
    parse_timestamp,
    sanitize_dict,
)
from tests.alteiatest import AlteiaTestBase

d1 = {"a": {"b": {"c": "d"}}}

d2 = {"a": {"b": {"c": "d", "e": "f"}}}

d3 = {"a": {"b": {"c": "g"}}}


class TestUtils(AlteiaTestBase):
    """Tests for utilities."""

    def test_sanitize_dict(self):
        dirty = {"key1$": ["$value1", {"key.2": "value2"}]}
        sanitize_dict(dirty)
        self.assertDictEqual(dirty, {"key1": ["$value1", {"key2": "value2"}]})

    def test_new_instance_existing(self):
        """Test instance creation for existing module and class."""
        instance = new_instance("alteia.core.config", "ConnectionConfig")
        self.assertNotEqual(instance, None)
        self.assertIsInstance(instance, ConnectionConfig)

    def test_new_instance_non_existing(self):
        """Test instance creation for non existing module or class."""
        with self.assertRaises(ConfigError):
            new_instance("blabla", class_name=None)

        with self.assertRaises(ConfigError):
            new_instance(module_path=None, class_name=None)

        with self.assertRaises(ConfigError):
            new_instance("alteia.core.config", "FakeClass")

        with self.assertRaises(ConfigError):
            new_instance("alteia.fake_module", "TestClass")

    def test_flatten(self):
        res = flatten_dict(copy.deepcopy(d1))
        self.assertEqual(res["a.b.c"], "d")

        d = {}
        res = flatten_dict(d)
        self.assertEqual(len(res), 0)

        d = {"a": "b"}

        res = flatten_dict(d)
        self.assertEqual(res["a"], "b")

    def test_find(self):
        self.assertEqual(find(copy.deepcopy(d1), "a.b.c"), "d")

    def test_merge_dict(self):
        res = dict_merge(copy.deepcopy(d1), copy.deepcopy(d2))
        self.assertEqual(res, {"a": {"b": {"c": "d", "e": "f"}}})

    def test_merge_dict_in_place(self):
        h = copy.deepcopy(d1)
        dict_merge(h, {"a": {"y": 2}})
        self.assertEqual(h, {"a": {"b": {"c": "d"}, "y": 2}})

    def test_merge_dict_with_add_keys(self):
        res = dict_merge(copy.deepcopy(d1), copy.deepcopy(d2), add_keys=False)
        self.assertEqual(res, {"a": {"b": {"c": "d"}}})

    def test_chunks(self):
        my_list = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]
        self.assertEqual(len(get_chunks(my_list, 10)), 3)
        self.assertEqual(len(get_chunks(my_list, 26)), 1)
        self.assertEqual(len(get_chunks(my_list, 30)), 1)

        results = []
        for chunk in get_chunks(my_list, 4):
            results += chunk
        self.assertEqual(results, my_list)


class TestParseTimestamp(AlteiaTestBase):
    def test_timestamp_with_time_zone_separator(self):
        timestamp = "2021-12-08T14:14:18.345541Z"
        self.assertEqual(
            parse_timestamp(timestamp),
            datetime.datetime(2021, 12, 8, 14, 14, 18, 345541),
        )

    def test_timestamp_with_time_zone_separator_microseconds(self):
        timestamp = "2021-12-08T14:14:18.345541374Z"
        self.assertEqual(
            parse_timestamp(timestamp),
            datetime.datetime(2021, 12, 8, 14, 14, 18, 345541),
        )

    def test_timestamp_with_tz_hours(self):
        timestamp = "2021-12-08T14:14:18.344673387+00:00"
        self.assertEqual(
            parse_timestamp(timestamp),
            datetime.datetime(2021, 12, 8, 14, 14, 18, 344673),
        )
