import functools
import inspect
import warnings
from typing import AnyStr, List

# Display deprecation warnings even if -Wd option is not set
warnings.simplefilter('default', category=DeprecationWarning)


def warn_for_deprecation(msg: AnyStr, *,
                         target: AnyStr = None):
    target_release = 'the {} release'.format(target) if target \
        else 'a forthcoming release'

    complete_msg = '{} will be removed in {}'.format(msg, target_release)
    warnings.warn(complete_msg, DeprecationWarning)


def deprecated(deprecated_kwargs: List[AnyStr] = None, target: AnyStr = None):
    """Decorator to warn about deprecation.

    It supports functions, methods and keyword arguments deprecation.

    """
    def deprecated_decorator(f):
        if inspect.ismethod(f):
            sig = '{}.{}()'.format(f.im_class.__name__, f.__name__)
        elif inspect.isfunction(f):
            sig = '{}.{}()'.format(f.__module__, f.__name__)
        else:
            sig = '{}()'.format(f.__name__)

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if deprecated_kwargs:
                _deprecated = [a for a in kwargs if a in deprecated_kwargs]
                if len(_deprecated) == 1:
                    msg = 'Support for {!r} parameter in {!r}'.format(
                        _deprecated, sig)
                elif len(_deprecated) > 1:
                    msg = 'Support for {!r} parameters in {!r}'.format(
                        _deprecated, sig)
                else:
                    msg = None
            else:
                msg = '{!r}'.format(sig)

            if msg:
                warn_for_deprecation(msg, target=target)

            return f(*args, **kwargs)

        return wrapped

    return deprecated_decorator
