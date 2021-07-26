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

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        try:
            h_data = h_visit(tup.blob.data.decode())
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                fn_data._asdict(),
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
                fn_name,
            )
            for fn_name, fn_data in h_data.functions
        ]
        result.append(
            Metric(
                self.name,
                h_data.total._asdict(),
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        )
        return result
