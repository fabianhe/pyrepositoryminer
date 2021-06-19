from typing import Awaitable, Callable, Dict, Iterable, Type

from pyrepositoryminer.metrics.nativeblob.halstead import Halstead
from pyrepositoryminer.metrics.nativeblob.linecount import Linecount
from pyrepositoryminer.metrics.nativeblob.maintainability import Maintainability
from pyrepositoryminer.metrics.nativeblob.nesting import Nesting
from pyrepositoryminer.metrics.nativeblob.raw import Raw
from pyrepositoryminer.metrics.structs import BlobTuple, Metric

Metrics: Dict[
    str,
    Type[Callable[[BlobTuple], Awaitable[Iterable[Metric]]]],
]

Metrics = {
    metric.name: metric  # type: ignore
    for metric in (Halstead, Raw, Maintainability, Linecount, Nesting)
}
