from abc import ABC, abstractmethod
from typing import Awaitable, Iterable, Optional, final

from pyrepositoryminer.metrics.structs import Metric, TreeTuple
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableObject,
    VisitableTree,
)


class NativeTreeVisitor(TreeVisitor):
    async def visitTree(self, tree: VisitableTree) -> None:
        self.tree: Optional[TreeTuple] = TreeTuple(tree, self.oid_is_cached(tree.id))
        self.cache_oid(tree.id)

    async def visitBlob(self, blob: VisitableBlob) -> None:
        pass

    async def __call__(self, visitable_object: VisitableObject) -> Optional[TreeTuple]:
        self.visited_commit = False
        self.tree = None
        await visitable_object.accept(self)
        return self.tree


class NativeTreeMetric(ABC):
    async def cache_hit(self, tree_tup: TreeTuple) -> Iterable[Metric]:
        return await self.analyze(tree_tup)

    @abstractmethod
    def analyze(self, tree_tup: TreeTuple) -> Awaitable[Iterable[Metric]]:
        pass

    @final
    async def __call__(self, tree_tup: TreeTuple) -> Iterable[Metric]:
        if tree_tup.is_cached:
            return await self.cache_hit(tree_tup)
        else:
            return await self.analyze(tree_tup)

    @classmethod
    @property
    def name(cls) -> str:
        return str(cls.__name__).lower()
