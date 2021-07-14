from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from typing import Iterable

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Linecount(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.is_binary())

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
        p = await create_subprocess_exec("wc", "-l", stdin=PIPE, stdout=PIPE)
        stdout, _ = await p.communicate(blob_tup.blob.data)
        result = [
            Metric(
                self.name,
                int(stdout),
                False,
                ObjectIdentifier(blob_tup.blob.id, blob_tup.path),
            )
        ]
        return result
