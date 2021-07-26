from pyrepositoryminer.metrics.diffblob.main import DiffBlobMetric
from pyrepositoryminer.metrics.nativeblob.pylinecount import Pylinecount


class Diffpylinecount(DiffBlobMetric):
    filter = Pylinecount.filter
    analyze = Pylinecount.analyze
