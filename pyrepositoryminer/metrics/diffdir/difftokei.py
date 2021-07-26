from pyrepositoryminer.metrics.diffdir.main import DiffDirMetric
from pyrepositoryminer.metrics.dir.tokei import Tokei


class DiffTokei(DiffDirMetric):
    analyze = Tokei.analyze
