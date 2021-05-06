from __future__ import annotations

from pyrepositoryminer.metrics.tree import TreeMetric, TreeMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class LOC(TreeMetric):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> LOC:
        self.n += 0 if blob.obj.is_binary else len(blob.obj.data.split(b"\n"))
        return self

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)
