from pyrepositoryminer.metrics.nativeblob.complexity import Complexity
from pyrepositoryminer.metrics.nativeblob.halstead import Halstead
from pyrepositoryminer.metrics.nativeblob.linecount import Linecount
from pyrepositoryminer.metrics.nativeblob.linelength import Linelength
from pyrepositoryminer.metrics.nativeblob.maintainability import Maintainability
from pyrepositoryminer.metrics.nativeblob.nesting import Nesting
from pyrepositoryminer.metrics.nativeblob.pylinecount import Pylinecount
from pyrepositoryminer.metrics.nativeblob.raw import Raw

Metrics = {
    metric.name: metric
    for metric in (
        Halstead,
        Raw,
        Maintainability,
        Linecount,
        Nesting,
        Complexity,
        Pylinecount,
        Linelength,
    )
}
