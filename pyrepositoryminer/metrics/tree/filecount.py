from typing import Dict

from pyrepositoryminer.metrics.tree import TreeMetric, TreeMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Filecount(TreeMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.n: int = 0

    def is_filtered(self, blob: VisitableBlob) -> bool:
        return False

    def analyze_blob(self, blob: VisitableBlob) -> None:
        self.n += 1

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)
