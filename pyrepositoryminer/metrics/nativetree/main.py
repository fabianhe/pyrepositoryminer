from abc import ABC
from typing import Optional

from pyrepositoryminer.metrics.main import BaseMetric
from pyrepositoryminer.metrics.structs import NativeTreeMetricInput
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableCommit,
    VisitableObject,
    VisitableTree,
)


class NativeTreeVisitor(TreeVisitor):
    async def visitCommit(self, commit: VisitableCommit) -> None:
        if self.visited_commit:
            return
        self.visited_commit = True
        self.commit = commit
        await commit.tree.accept(self)

    async def visitTree(self, tree: VisitableTree) -> None:
        self.tree: Optional[NativeTreeMetricInput] = NativeTreeMetricInput(
            self.oid_is_cached(tree.id), tree, self.commit
        )
        self.cache_oid(tree.id)

    async def visitBlob(self, blob: VisitableBlob) -> None:
        pass

    async def __call__(
        self, visitable_object: VisitableObject
    ) -> Optional[NativeTreeMetricInput]:
        self.visited_commit = False
        self.tree = None
        await visitable_object.accept(self)
        return self.tree


class NativeTreeMetric(BaseMetric[NativeTreeMetricInput], ABC):
    pass
