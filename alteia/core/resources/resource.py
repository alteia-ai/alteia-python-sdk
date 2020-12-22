import copy
from types import SimpleNamespace
from typing import List, NamedTuple


class Resource(SimpleNamespace):
    def __init__(self, *, id: str = None, __remove_undefined: bool = True, **kwargs):
        """Resource class.

        Args:
            id: Resource identifier (if missing, ``_id`` must be defined).

            __remove_undefined: Optional option to remove undefined properties before
                storing it in the Resource (default is ``True``).

            **kwargs: Keyword arguments to initialize the resource properties.

        Returns:
            Resource: Resource created.

        """
        if id is None:
            if kwargs.get('_id') is None:
                raise KeyError('"_id" or "id" must be defined')
            else:
                id = kwargs['_id']
        else:
            # Duplicate ``id`` into ``_id`` for retrocompatibility
            kwargs['_id'] = id

        if __remove_undefined:
            temp_dict = copy.deepcopy(kwargs)
            # Remove properties whose value is ``None``
            for key, value in temp_dict.items():
                if value is None:
                    del kwargs[key]

        super().__init__(id=id, **kwargs)

    @property
    def _desc(self):
        # For retrocompatibility
        return self.__dict__

    def __repr__(self):
        return f"{self.__class__.__name__}(_id='{self._id}')"


ResourcesWithTotal = NamedTuple(
    'ResourcesWithTotal',
    [('total', int), ('results', List[Resource])]
)
