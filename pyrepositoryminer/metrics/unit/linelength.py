from __future__ import annotations

from typing import Dict, Iterable, List

from pyrepositoryminer.metrics.unit import UnitMetric, UnitMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Linelength(UnitMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[UnitMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Linelength:
        if blob.obj.is_binary:
            return self
        for i, line in enumerate(blob.obj.data.split(b"\n")):
            self.metrics.append(
                UnitMetricOutput(
                    len(line),
                    blob_id=blob.obj.id,
                    unit_id=f"L{i+1}",
                    blob_name=self.pathname,
                )
            )
        return self

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        return self.metrics
