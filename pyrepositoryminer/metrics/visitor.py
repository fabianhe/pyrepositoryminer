from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, Awaitable, List, Set, Union

from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableCommit,
    VisitableObject,
    VisitableTree,
)


class TreeVisitor(ABC):
    def __init__(self) -> None:
        self.oid_cache: Set[str] = set()
        self.path: List[str] = []
        self.visited_commit: bool = False

    @property
    def pathname(self) -> str:
        return "/".join(self.path)

    def oid_is_cached(self, oid: str) -> bool:
        return oid in self.oid_cache

    def cache_oid(self, oid: str) -> None:
        self.oid_cache.add(oid)

    async def visitCommit(self, commit: VisitableCommit) -> None:
        if self.visited_commit:
            return
        self.visited_commit = True
        await commit.tree.accept(self)

    @abstractmethod
    async def visitTree(self, tree: VisitableTree) -> None:
        pass

    @abstractmethod
    async def visitBlob(self, blob: VisitableBlob) -> None:
        pass

    @abstractmethod
    def __call__(
        self, visitable_object: VisitableObject
    ) -> Union[Awaitable[Any], AsyncIterable[Any]]:
        pass
