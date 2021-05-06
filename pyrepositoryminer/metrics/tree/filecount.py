from __future__ import annotations

from pyrepositoryminer.metrics.tree import TreeMetric, TreeMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Filecount(TreeMetric):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> Filecount:
        self.n += 1
        return self

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)
