from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from pygit2 import Blob, Commit, Object, Tree

if TYPE_CHECKING:
    from pyrepositoryminer.metrics.visitor import TreeVisitor


class VisitableObject:
    @classmethod
    def from_object(cls, obj: Object) -> VisitableObject:
        if isinstance(obj, Tree):
            return VisitableTree(obj)
        elif isinstance(obj, Blob):
            return VisitableBlob(obj)
        elif isinstance(obj, Commit):
            return VisitableCommit(obj)
        return VisitableObject(obj)

    def __init__(self, obj: Object) -> None:
        self.obj = obj

    async def accept(self, treevisitor: "TreeVisitor") -> None:
        pass

    @property
    def id(self) -> str:
        return str(self.obj.id)

    @property
    def name(self) -> str:
        return str(self.obj.name)


class VisitableCommit(VisitableObject):
    async def accept(self, treevisitor: "TreeVisitor") -> None:
        await treevisitor.visitCommit(self)

    @property
    def tree(self) -> VisitableTree:
        return VisitableTree(self.obj.tree)


class VisitableTree(VisitableObject):
    async def accept(self, treevisitor: "TreeVisitor") -> None:
        await treevisitor.visitTree(self)

    def __iter__(self) -> Iterator[VisitableObject]:
        return (VisitableObject.from_object(obj) for obj in self.obj)


class VisitableBlob(VisitableObject):
    async def accept(self, treevisitor: "TreeVisitor") -> None:
        await treevisitor.visitBlob(self)

    @property
    def is_binary(self) -> bool:
        return bool(self.obj.is_binary)

    @property
    def data(self) -> bytes:
        return bytes(self.obj.data)

    @property
    def size(self) -> int:
        return int(self.obj.size)
