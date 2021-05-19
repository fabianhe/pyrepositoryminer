from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Tuple, final

from pyrepositoryminer.metrics.blob import BlobMetricOutput
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import VisitableBlob


class UnitMetricOutput(BlobMetricOutput):
    unit_id: str


class UnitMetric(TreeVisitor, ABC):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[UnitMetricOutput] = []

    @abstractmethod
    def analyze_unit_values(self, blob: VisitableBlob) -> Iterable[Tuple[str, Any]]:
        pass

    @final
    def handle_cache_hit(self, blob: VisitableBlob) -> None:
        self.metrics.append(
            UnitMetricOutput(
                value=None,
                cached=True,
                unit_id="",
                blob_id=str(blob.obj.id),
                blob_name=self.pathname,
            )
        )

    @final
    def analyze_blob(self, blob: VisitableBlob) -> None:
        self.metrics.extend(
            UnitMetricOutput(
                unit_id=unit_id,
                value=value,
                blob_id=str(blob.obj.id),
                blob_name=self.pathname,
            )
            for unit_id, value in self.analyze_unit_values(blob)
        )

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        yield from self.metrics
