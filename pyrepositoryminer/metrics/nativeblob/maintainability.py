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

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        try:
            mi_data = mi_visit(tup.blob.data.decode(), multi=True)
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                float(mi_data),
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        ]
        return result
