from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, FrozenSet, Iterable, List

from pygit2 import Blob, Oid, Tree

from pyrepositoryminer.visitableobject import VisitableBlob, VisitableTree


class TreeVisitor(ABC):
    def __init__(self, previous_ids: Iterable[Oid] = []) -> None:
        self.previous_ids: FrozenSet[Oid] = frozenset(previous_ids)
        self.path: List[str] = []

    @property
    def pathname(self) -> str:
        return "".join(self.path)

    @abstractmethod
    def visitBlob(self, blob: VisitableBlob) -> TreeVisitor:
        pass

    def visitTree(self, tree: VisitableTree) -> TreeVisitor:
        unseen = (obj for obj in tree.obj if obj.id not in self.previous_ids)
        for obj in unseen:
            if isinstance(obj, Tree):
                self.path.append(f"{obj.name}/")
                VisitableTree(obj).accept(self)
            elif isinstance(obj, Blob):
                self.path.append(str(obj.name))
                VisitableBlob(obj).accept(self)
            self.path.pop(-1)
        return self

    @property
    @abstractmethod
    def result(self) -> Any:
        pass
