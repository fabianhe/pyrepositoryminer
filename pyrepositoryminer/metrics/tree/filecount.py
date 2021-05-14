from __future__ import annotations

from typing import Dict

from pyrepositoryminer.metrics.tree import TreeMetric, TreeMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Filecount(TreeMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> Filecount:
        self.n += 1
        return self

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)
