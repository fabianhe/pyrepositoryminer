from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pygit2 import Blob, Object, Tree

if TYPE_CHECKING:
    from pyrepositoryminer.metrics.visitor import TreeVisitor


class VisitableObject(ABC):
    @abstractmethod
    def __init__(self, obj: Object) -> None:
        pass

    @abstractmethod
    def accept(self, treevisitor: "TreeVisitor") -> None:
        pass


class VisitableTree(VisitableObject):
    def __init__(self, obj: Tree) -> None:
        super().__init__(obj)
        self.obj: Tree = obj

    def accept(self, treevisitor: "TreeVisitor") -> None:
        treevisitor.visitTree(self)


class VisitableBlob(VisitableObject):
    def __init__(self, obj: Blob) -> None:
        super().__init__(obj)
        self.obj: Blob = obj

    def accept(self, treevisitor: "TreeVisitor") -> None:
        treevisitor.visitBlob(self)
