from __future__ import annotations

from typing import Iterable, List

from radon.metrics import mi_visit

from pyrepositoryminer.metrics.blob import BlobMetric, BlobMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Maintainability(BlobMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Maintainability:
        if blob.obj.name.endswith(".py"):
            self.metrics.append(
                BlobMetricOutput(
                    value=mi_visit(blob.obj.data.decode(), multi=True),
                    blob_id=blob.obj.id,
                )
            )

        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics
