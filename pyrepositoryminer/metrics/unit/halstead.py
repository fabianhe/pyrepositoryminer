from __future__ import annotations

from typing import Dict, Iterable, List

from radon.metrics import h_visit

from pyrepositoryminer.metrics.unit import UnitMetric, UnitMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Halstead(UnitMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[UnitMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Halstead:
        if blob.obj.name.endswith(".py"):
            self.metrics.extend(
                UnitMetricOutput(
                    unit_id=str(function_name),
                    value=report._asdict(),
                    blob_id=blob.obj.id,
                    blob_name=self.pathname,
                )
                for function_name, report in h_visit(blob.obj.data).functions
            )

        return self

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        return self.metrics
