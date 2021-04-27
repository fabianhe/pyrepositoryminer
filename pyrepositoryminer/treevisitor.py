from abc import ABC, abstractmethod
from typing import Any

from pygit2 import Blob, Tree

from .visitableobject import VisitableBlob, VisitableTree


class TreeVisitor(ABC):
    @abstractmethod
    def visitBlob(self, blob: VisitableBlob) -> None:
        pass

    def visitTree(self, tree: VisitableTree) -> None:
        for obj in tree.obj:
            if isinstance(obj, Tree):
                VisitableTree(obj).accept(self)
            elif isinstance(obj, Blob):
                VisitableBlob(obj).accept(self)

    @property
    @abstractmethod
    def result(self) -> Any:
        pass


class LocVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> None:
        if not blob.obj.is_binary:
            self.n += len(blob.obj.data.split(b"\n"))

    @property
    def result(self) -> int:
        return self.n


class FilecountVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> None:
        self.n += 1

    @property
    def result(self) -> int:
        return self.n
