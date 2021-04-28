from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from pygit2 import Blob, Tree
from radon.complexity import cc_visit
from radon.raw import Module, analyze

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


class ComplexityVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.complexities: List[Tuple[str, str]] = []

    def visitBlob(self, blob: VisitableBlob) -> None:
        if blob.obj.name.endswith(".py"):
            if complexities := cc_visit(blob.obj.data):
                self.complexities.append(
                    (blob.obj.id, max(obj.complexity for obj in complexities))
                )

    @property
    def result(self) -> List[Tuple[str, str]]:
        return self.complexities


class RawVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[Module] = []

    def visitBlob(self, blob: VisitableBlob) -> None:
        if blob.obj.name.endswith(".py"):
            data: Module = analyze(blob.obj.data.decode())
            self.metrics.append(data)

    @property
    def result(self) -> List[Module]:
        return self.metrics
