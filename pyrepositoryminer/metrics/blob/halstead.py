from __future__ import annotations

from typing import Dict, Iterable, List

from radon.metrics import h_visit

from pyrepositoryminer.metrics.blob import BlobMetric, BlobMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Halstead(BlobMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Halstead:
        if blob.obj.name.endswith(".py"):
            data = h_visit(blob.obj.data.decode())
            self.metrics.append(
                BlobMetricOutput(
                    value=data.total._asdict(),
                    blob_id=blob.obj.id,
                    blob_name=self.pathname,
                )
            )

        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics
