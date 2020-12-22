from typing import List, NamedTuple

from alteia.core.utils.typing import ShareToken

ShareTokensWithTotal = NamedTuple(
    'ShareTokensWithTotal',
    [('total', int), ('results', List[ShareToken])]
)
