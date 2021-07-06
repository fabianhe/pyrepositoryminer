from typing import Iterable

from radon.complexity import cc_visit

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Complexity(NativeBlobMetric):
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
            cc_data = cc_visit(blob_tup.blob.data)
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                subobject.complexity,
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
                subobject.fullname,
            )
            for subobject in cc_data
        ]
        return result
