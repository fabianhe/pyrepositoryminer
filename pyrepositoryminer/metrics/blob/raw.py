from __future__ import annotations

from typing import Iterable, List

from radon.raw import Module, analyze

from pyrepositoryminer.metrics.blob import BlobMetric, BlobMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Raw(BlobMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Raw:
        if blob.obj.name.endswith(".py"):
            data: Module = analyze(blob.obj.data.decode())
            self.metrics.append(
                BlobMetricOutput(
                    value=data._asdict(),
                    blob_id=blob.obj.id,
                )
            )

        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics
