from typing import Dict

from pyrepositoryminer.metrics.tree import TreeMetric, TreeMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class LOC(TreeMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.n: int = 0

    def is_filtered(self, blob: VisitableBlob) -> bool:
        return bool(blob.obj.is_binary)

    def analyze_blob(self, blob: VisitableBlob) -> None:
        self.n += len(blob.obj.data.split(b"\n"))

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)
