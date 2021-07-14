from typing import Iterable

from radon.metrics import mi_visit

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Maintainability(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.endswith(".py"))

    async def cache_hit(self, blob_tup: NativeBlobMetricInput) -> Iterable[Metric]:
        return [
            Metric(
                self.name,
                None,
                True,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        ]

    async def analyze(self, blob_tup: NativeBlobMetricInput) -> Iterable[Metric]:
        try:
            mi_data = mi_visit(blob_tup.blob.data.decode(), multi=True)
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                float(mi_data),
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        ]
        return result
