from __future__ import annotations

from typing import Dict, Iterable, List

from radon.raw import analyze

from pyrepositoryminer.metrics.blob import BlobMetric, BlobMetricOutput
from pyrepositoryminer.visitableobject import VisitableBlob


class Raw(BlobMetric):
    def __init__(self, cache: Dict[str, bool]) -> None:
        super().__init__(cache)
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> Raw:
        if not blob.obj.name.endswith(".py"):
            return self
        id = str(blob.obj.id)
        if self.cached_oids.setdefault(id, False):
            self.metrics.append(
                BlobMetricOutput(value="-", blob_id=id, blob_name=self.pathname)
            )
            return self
        self.cached_oids[id] = True
        self.metrics.append(
            BlobMetricOutput(
                value=analyze(blob.obj.data.decode())._asdict(),
                blob_id=id,
                blob_name=self.pathname,
            )
        )
        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics
