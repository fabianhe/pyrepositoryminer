from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pygit2 import Blob, Tree

from pyrepositoryminer.visitableobject import VisitableBlob, VisitableTree


class TreeVisitor(ABC):
    def __init__(self, cache: Dict[str, bool]) -> None:
        self.cached_oids = cache
        self.path: List[str] = []

    @property
    def pathname(self) -> str:
        return "".join(self.path)

    @abstractmethod
    def visitBlob(self, blob: VisitableBlob) -> TreeVisitor:
        pass

    def visitTree(self, tree: VisitableTree) -> TreeVisitor:
        for obj in tree.obj:
            id = str(obj.id)
            if isinstance(obj, Tree):
                self.path.append(f"{obj.name}/")
                self.cached_oids.setdefault(id, False)
                VisitableTree(obj).accept(self)
                self.cached_oids[id] = True
            elif isinstance(obj, Blob):
                self.path.append(str(obj.name))
                VisitableBlob(obj).accept(self)
            self.path.pop(-1)
        return self

    @property
    @abstractmethod
    def result(self) -> Any:
        pass
