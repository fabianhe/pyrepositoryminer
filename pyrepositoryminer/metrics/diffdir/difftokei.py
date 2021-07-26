from typing import Iterable

from pyrepositoryminer.metrics.diffdir.main import DiffDirMetric
from pyrepositoryminer.metrics.dir.tokei import tokei
from pyrepositoryminer.metrics.structs import DirMetricInput, Metric


class DiffTokei(DiffDirMetric):
    async def analyze(self, tup: DirMetricInput) -> Iterable[Metric]:
        return await tokei(self.name, tup.path, tup.tree)
