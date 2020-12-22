from logging.config import fileConfig
from unittest import TestCase
from unittest.mock import Mock, call

from pkg_resources import resource_filename

if not hasattr(Mock, 'assert_called_once'):
    # Mock.assert_called_once() was introduced in Python 3.6
    def __mock_assert_called_once(self, *args, **kwargs):
        return call(*args, **kwargs) in self.call_args_list
    Mock.assert_called_once = __mock_assert_called_once


class AlteiaTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        fileConfig(resource_filename(__name__, 'logging-test.conf'),
                   disable_existing_loggers=False)

    def assertEqualCoordinates(self, a, b, places=7, msg=None,
                               delta=None):
        """Test that ``a`` and ``b`` are almost equal lists of numbers.

        Lists can be nested.

        """
        if type(a) != type(b):
            msg = '{} and {} have different type'
            raise self.failureException(msg.format(a, b))

        if type(a) == 'list':
            if len(a) != len(b):
                msg = '{} and {} have different length'
                raise self.failureException(msg.format(a, b))

            for i in range(len(a)):
                self.assertEqualCoordinates(a[i], b[i], places=places,
                                            msg=msg, delta=delta)
        elif type(a) in ('int', 'float'):
            self.assertAlmostEqual(a, b, places, msg, delta)
