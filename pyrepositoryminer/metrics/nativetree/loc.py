from typing import Iterable, List

from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric
from pyrepositoryminer.metrics.structs import Metric, TreeTuple
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableObject,
    VisitableTree,
)


class Loc(NativeTreeMetric):
    async def analyze(self, tree_tup: TreeTuple) -> Iterable[Metric]:
        n = 0
        q: List[VisitableObject] = [tree_tup.tree]
        while q:
            obj = q.pop(0)
            if isinstance(obj, VisitableBlob):
                if obj.is_binary:
                    continue
                n += obj.data.count(b"\n") + 1
            elif isinstance(obj, VisitableTree):
                q.extend(list(obj))
        return [Metric(self.name, n, False)]
