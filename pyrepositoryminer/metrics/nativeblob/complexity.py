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

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        try:
            cc_data = cc_visit(tup.blob.data)
        except (SyntaxError, UnicodeDecodeError):
            return []  # TODO get an error output?
        result = [
            Metric(
                self.name,
                subobject.complexity,
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
                subobject.fullname,
            )
            for subobject in cc_data
        ]
        return result
