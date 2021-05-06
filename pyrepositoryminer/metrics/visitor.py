from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pygit2 import Blob, Tree

from pyrepositoryminer.visitableobject import VisitableBlob, VisitableTree


class TreeVisitor(ABC):
    @abstractmethod
    def visitBlob(self, blob: VisitableBlob) -> TreeVisitor:
        pass

    def visitTree(self, tree: VisitableTree) -> TreeVisitor:
        for obj in tree.obj:
            if isinstance(obj, Tree):
                VisitableTree(obj).accept(self)
            elif isinstance(obj, Blob):
                VisitableBlob(obj).accept(self)
        return self

    @property
    @abstractmethod
    def result(self) -> Any:
        pass
