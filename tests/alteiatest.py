import os
from logging.config import fileConfig
from unittest import TestCase


class AlteiaTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        fileConfig(
            os.path.join(os.path.dirname(__file__), "logging-test.conf"),
            disable_existing_loggers=False,
        )

    def assertEqualCoordinates(self, a, b, places=7, msg=None, delta=None):
        """Test that ``a`` and ``b`` are almost equal lists of numbers.

        Lists can be nested.

        """
        if not isinstance(a, type(b)):
            msg = "{} and {} have different type"
            raise self.failureException(msg.format(a, b))

        if isinstance(a, list):
            if len(a) != len(b):
                msg = "{} and {} have different length"
                raise self.failureException(msg.format(a, b))

            for i in range(len(a)):
                self.assertEqualCoordinates(a[i], b[i], places=places, msg=msg, delta=delta)
        elif isinstance(a, (int, float)):
            self.assertAlmostEqual(a, b, places, msg, delta)
