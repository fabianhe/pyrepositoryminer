from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, final

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
    def is_filtered(self, blob: VisitableBlob) -> bool:
        """Check whether a blob is filtered."""
        pass

    def is_cached(self, blob: VisitableBlob) -> bool:
        """Check whether a blob is cached."""
        return self.cached_oids.setdefault(str(blob.obj.id), False)

    def cache_blob(self, blob: VisitableBlob) -> None:
        """Cache a blob."""
        self.cached_oids[str(blob.obj.id)] = True

    @abstractmethod
    def handle_cache_hit(self, blob: VisitableBlob) -> None:
        pass

    @abstractmethod
    def analyze_blob(self, blob: VisitableBlob) -> None:
        """Analyze a blob."""
        pass

    @final
    def visitBlob(self, blob: VisitableBlob) -> TreeVisitor:
        if self.is_filtered(blob):
            return self
        elif self.is_cached(blob):
            self.handle_cache_hit(blob)
            return self
        self.cache_blob(blob)
        self.analyze_blob(blob)
        return self

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
            else:
                continue
            self.path.pop(-1)
        return self

    @property
    @abstractmethod
    def result(self) -> Any:
        pass
