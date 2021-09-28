from typing import Iterable

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Linelength(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.is_binary())

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        result = [
            Metric(
                self.name,
                len(line),
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
                f"L{i+1}",
            )
            for i, line in enumerate(tup.blob.obj.data.split(b"\n"))
        ]
        return result
