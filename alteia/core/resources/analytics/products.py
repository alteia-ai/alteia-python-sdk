"""Product related resources.

"""

from datetime import datetime
from typing import List, NamedTuple


class ProductLog:
    def __init__(self, *, timestamp: datetime, record: dict):
        self.timestamp = timestamp
        self.record = record


ProductLogsWithTotal = NamedTuple(
    'ProductLogsWithTotal',
    [('total', int), ('logs', List[ProductLog])]
)
