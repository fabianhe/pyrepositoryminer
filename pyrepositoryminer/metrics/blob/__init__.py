from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, final

from pyrepositoryminer.metrics.tree import TreeMetricOutput
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import VisitableBlob


class BlobMetricOutput(TreeMetricOutput):
    blob_id: str
    blob_name: str


class BlobMetric(TreeVisitor, ABC):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[BlobMetricOutput] = []

    @abstractmethod
    def analyze_blob_value(self, blob: VisitableBlob) -> Any:
        pass

    @final
    def analyze_blob(self, blob: VisitableBlob) -> None:
        self.metrics.append(
            BlobMetricOutput(
                value=self.analyze_blob_value(blob),
                blob_id=str(blob.obj.id),
                blob_name=self.pathname,
            )
        )

    @final
    def handle_cache_hit(self, blob: VisitableBlob) -> None:
        self.metrics.append(
            BlobMetricOutput(
                value=None,
                cached=True,
                blob_id=str(blob.obj.id),
                blob_name=self.pathname,
            )
        )

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        yield from self.metrics
