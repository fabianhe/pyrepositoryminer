from typing import Iterable

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import BlobTuple, Metric, ObjectIdentifier


class Pylinecount(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.is_binary())

    async def cache_hit(self, blob_tup: BlobTuple) -> Iterable[Metric]:
        return [
            Metric(
                self.name,
                None,
                True,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        ]

    async def analyze(self, blob_tup: BlobTuple) -> Iterable[Metric]:
        result = [
            Metric(
                self.name,
                blob_tup.blob.obj.data.count(b"\n") + 1,
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        ]
        return result
