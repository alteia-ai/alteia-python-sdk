import collections
import hashlib
import importlib
from getpass import getpass
from typing import Optional

from alteia.core.errors import ConfigError

BLOCK_SIZE = 4096


def sanitize_dict(value):
    """Recursively remove special characters from dictionary keys.

    The special characters are . and $, eg the special characters for
    MongoDB.

    Note that, in case of key collision after the removal of special
    characters, the common key will be updated with the value of the
    renamed key.

    """
    if isinstance(value, dict):
        original_keys = [key for key in value.keys()]
        for key in original_keys:
            try:
                cleaned = key.translate({ord(c): None for c in '$.'})
            except TypeError:
                cleaned = key.translate(None,
                                        '$.')  # Note that translate() signature changes with key  # type but one  #
                # can't use isinstance since, in Python3,  # key may be of type str or bytes; In Python2 it  # will
                #  be unicode or str.
            value[cleaned] = sanitize_dict(value.pop(key))
    elif isinstance(value, list):
        for item in value:
            sanitize_dict(item)
    return value


def md5(file_path):
    """
    md5sum of the object
    used for uploads
    """
    object_hash = hashlib.md5()
    with open(file_path, 'rb') as fstr:
        for chunk in iter(lambda: fstr.read(BLOCK_SIZE), b''):
            object_hash.update(chunk)
    return object_hash.hexdigest()


def new_instance(module_path, class_name, **kwargs):
    """
    dynamically load a class from a string and return an new instance of this class
    """
    # module path and class name have to be provided to get the class and create a new instance
    if not module_path:
        raise ConfigError('The module path is either null or empty and has to be provided to create a new instance')
    if not class_name:

        raise ConfigError('The class name is either null or empty and has to be provided to create a new instance')

    try:
        return getattr(importlib.import_module(module_path), class_name)(**kwargs)
    except Exception:
        raise ConfigError(
            'Some errors occurred while getting a new instance of the class {module_path}.{class_name}'.format(
                module_path=module_path, class_name=class_name))


def dict_merge(dct, merge_dct, add_keys=True):
    """Recursive dict merge.

    Inspired by :meth:``dict.update()``, instead of updating only
    top-level keys, dict_merge recurses down into dicts nested to an
    arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict): onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys

    Returns:
        dict: Updated dictionary.

    """
    if not add_keys:
        merge_dct = {
            k: merge_dct[k] for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.abc.Mapping)):
            dct[k] = dict_merge(dct[k], merge_dct[k], add_keys=add_keys)
        else:
            dct[k] = merge_dct[k]

    return dct


def flatten_dict(dd, separator='.', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


def find(dict, str, separator='.'):
    keys = str.split(separator)
    rv = dict
    for key in keys:
        rv = rv[key]
    return rv


def get_full_class_path(o):
    """Returns the full class path of an object"""
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + o.__class__.__name__


def prompt_user(prompt: str, current_value: Optional[str], hidden: bool = False) -> str:
    if current_value is not None:
        if hidden:
            prompt += ' [or press ENTER to leave the current value]'
        else:
            prompt += f' [or press ENTER to leave {current_value}]'
    prompt += ': '
    if hidden:
        user_value = getpass(prompt) or ''
    else:
        user_value = input(prompt)
    if not user_value:
        user_value = current_value
    return user_value
