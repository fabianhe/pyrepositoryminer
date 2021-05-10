from __future__ import annotations

from typing import Iterable, List

from radon.complexity import cc_visit

from pyrepositoryminer.metrics.unit import UnitMetric, UnitMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Complexity(UnitMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[UnitMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Complexity:
        if blob.obj.name.endswith(".py"):
            if complexities := cc_visit(blob.obj.data):
                self.metrics.extend(
                    UnitMetricOutput(
                        unit_id=str(u.fullname),
                        value=int(u.complexity),
                        blob_id=blob.obj.id,
                    )
                    for u in complexities
                )

        return self

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        return self.metrics
