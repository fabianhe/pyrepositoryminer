from typing import Dict, Type

from pyrepositoryminer.metrics.blob import BlobMetric
from pyrepositoryminer.metrics.blob.halstead import Halstead as HalsteadTotal
from pyrepositoryminer.metrics.blob.maintainability import Maintainability
from pyrepositoryminer.metrics.blob.nesting import Nesting
from pyrepositoryminer.metrics.blob.raw import Raw
from pyrepositoryminer.metrics.tree import TreeMetric
from pyrepositoryminer.metrics.tree.filecount import Filecount
from pyrepositoryminer.metrics.tree.loc import LOC
from pyrepositoryminer.metrics.unit import UnitMetric
from pyrepositoryminer.metrics.unit.complexity import Complexity
from pyrepositoryminer.metrics.unit.halstead import Halstead
from pyrepositoryminer.metrics.unit.linelength import Linelength

TreeMetrics: Dict[str, Type[TreeMetric]] = {"filecount": Filecount, "loc": LOC}
BlobMetrics: Dict[str, Type[BlobMetric]] = {
    "nesting": Nesting,
    "raw": Raw,
    "halstead_total": HalsteadTotal,
    "maintainability": Maintainability,
}
UnitMetrics: Dict[str, Type[UnitMetric]] = {
    "complexity": Complexity,
    "linelength": Linelength,
    "halstead": Halstead,
}
