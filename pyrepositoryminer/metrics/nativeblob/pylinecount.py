from typing import Iterable

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Pylinecount(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.is_binary())

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        result = [
            Metric(
                self.name,
                tup.blob.obj.data.count(b"\n") + 1,
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        ]
        return result
