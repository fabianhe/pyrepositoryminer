from typing import Awaitable, Callable, Dict, Iterable, Type

from pyrepositoryminer.metrics.nativeblob.halstead import Halstead
from pyrepositoryminer.metrics.structs import BlobTuple, Metric

Metrics: Dict[
    str,
    Type[Callable[[BlobTuple], Awaitable[Iterable[Metric]]]],
]

Metrics = {"halstead": Halstead}
