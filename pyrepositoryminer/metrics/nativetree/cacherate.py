from typing import Dict, Iterable, List, Set

from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric
from pyrepositoryminer.metrics.structs import Metric, TreeTuple
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableObject,
    VisitableTree,
)


class CacheRate(NativeTreeMetric):
    def __init__(self) -> None:
        self.cache: Set[str] = set()

    async def analyze(self, tree_tup: TreeTuple) -> Iterable[Metric]:
        rate: Dict[str, Dict[bool, int]] = {
            "blobs": {True: 0, False: 0},
            "trees": {True: 0, False: 0},
            "other": {True: 0, False: 0},
        }
        q: List[VisitableObject] = [tree_tup.tree]
        while q:
            obj = q.pop(0)
            is_cached = obj.id in self.cache
            if isinstance(obj, VisitableTree):
                q.extend(list(obj))
                rate["trees"][is_cached] += 1
            elif isinstance(obj, VisitableBlob):
                rate["blobs"][is_cached] += 1
            else:
                rate["other"][is_cached] += 1
            self.cache.add(obj.id)
        return [Metric(self.name, rate, False)]
