from typing import Iterable, List

from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric
from pyrepositoryminer.metrics.structs import Metric, NativeTreeMetricInput
from pyrepositoryminer.pobjects import Blob, Object, Tree


class Loc(NativeTreeMetric):
    async def analyze(self, tup: NativeTreeMetricInput) -> Iterable[Metric]:
        n = 0
        q: List[Object] = [tup.tree]
        while q:
            obj = q.pop(0)
            if isinstance(obj, Blob):
                if obj.is_binary:
                    continue
                n += obj.data.count(b"\n") + 1
            elif isinstance(obj, Tree):
                q.extend(list(obj))
        return [Metric(self.name, n, False)]
