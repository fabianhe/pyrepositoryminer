from typing import Iterable

from radon.metrics import h_visit

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Halstead(NativeBlobMetric):
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
            h_data = h_visit(blob_tup.blob.data.decode())
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                fn_data._asdict(),
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
                fn_name,
            )
            for fn_name, fn_data in h_data.functions
        ]
        result.append(
            Metric(
                self.name,
                h_data.total._asdict(),
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        )
        return result
