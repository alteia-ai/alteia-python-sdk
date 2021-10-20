import functools
import inspect
import warnings
from typing import List

# Display deprecation warnings even if -Wd option is not set
warnings.simplefilter('default', category=DeprecationWarning)


def warn_for_deprecation(msg: str, *, target: str = None):
    target_release = f'the {target} release' if target else 'a forthcoming release'

    complete_msg = f'{msg} will be removed in {target_release}'
    warnings.warn(complete_msg, DeprecationWarning)


def deprecated(deprecated_kwargs: List[str] = None, target: str = None):
    """Decorator to warn about deprecation.

    It supports functions, methods and keyword arguments deprecation.

    """
    def deprecated_decorator(f):
        if inspect.ismethod(f):
            sig = f'{f.im_class.__name__}.{f.__name__}()'
        elif inspect.isfunction(f):
            sig = f'{f.__module__}.{f.__name__}()'
        else:
            sig = f'{f.__name__}()'

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if deprecated_kwargs:
                _deprecated = [a for a in kwargs if a in deprecated_kwargs]
                if len(_deprecated) == 1:
                    msg = f'Support for {_deprecated!r} parameter in {sig!r}'
                elif len(_deprecated) > 1:
                    msg = f'Support for {_deprecated!r} parameters in {sig!r}'
                else:
                    msg = None
            else:
                msg = f'{sig!r}'

            if msg:
                warn_for_deprecation(msg, target=target)

            return f(*args, **kwargs)

        return wrapped

    return deprecated_decorator
