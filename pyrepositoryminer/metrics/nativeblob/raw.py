from typing import Iterable

from radon.raw import analyze

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Raw(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.endswith(".py"))

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        try:
            r_data = analyze(tup.blob.data.decode())
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                r_data._asdict(),
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        ]
        return result
