from __future__ import annotations

from abc import ABC, abstractmethod
from ast import (
    AST,
    Break,
    Continue,
    ExceptHandler,
    For,
    If,
    NodeVisitor,
    Try,
    While,
    With,
    parse,
    withitem,
)
from typing import Any, List, Tuple

from pygit2 import Blob, Oid, Tree
from radon.complexity import cc_visit
from radon.raw import Module, analyze

from .visitableobject import VisitableBlob, VisitableTree


class NestingASTVisitor(NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0
        self.max_n: int = self.n

    def visit(self, node: AST) -> NestingASTVisitor:
        self.max_n = max(self.max_n, self.n)
        super().visit(node)
        return self

    def nesting_visit(self, node: AST) -> None:
        self.n += 1
        super().generic_visit(node)
        self.n -= 1

    def visit_If(self, node: If) -> None:
        return self.nesting_visit(node)

    def visit_For(self, node: For) -> None:
        return self.nesting_visit(node)

    def visit_While(self, node: While) -> None:
        return self.nesting_visit(node)

    def visit_Break(self, node: Break) -> None:
        return self.nesting_visit(node)

    def visit_Continue(self, node: Continue) -> None:
        return self.nesting_visit(node)

    def visit_Try(self, node: Try) -> None:
        return self.nesting_visit(node)

    def visit_ExceptHandler(self, node: ExceptHandler) -> None:
        return self.nesting_visit(node)

    def visit_With(self, node: With) -> None:
        return self.nesting_visit(node)

    def visit_withitem(self, node: withitem) -> None:
        return self.nesting_visit(node)

    @property
    def result(self) -> int:
        return self.max_n


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


class LocVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> LocVisitor:
        if not blob.obj.is_binary:
            self.n += len(blob.obj.data.split(b"\n"))
        return self

    @property
    def result(self) -> int:
        return self.n


class FilecountVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> FilecountVisitor:
        self.n += 1
        return self

    @property
    def result(self) -> int:
        return self.n


class ComplexityVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.complexities: List[Tuple[Oid, str]] = []

    def visitBlob(self, blob: VisitableBlob) -> ComplexityVisitor:
        if blob.obj.name.endswith(".py"):
            if complexities := cc_visit(blob.obj.data):
                self.complexities.append(
                    (blob.obj.id, max(obj.complexity for obj in complexities))
                )
        return self

    @property
    def result(self) -> List[Tuple[Oid, str]]:
        return self.complexities


class RawVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[Tuple[Oid, Module]] = []

    def visitBlob(self, blob: VisitableBlob) -> RawVisitor:
        if blob.obj.name.endswith(".py"):
            data: Module = analyze(blob.obj.data.decode())
            self.metrics.append((blob.obj.id, data))
        return self

    @property
    def result(self) -> List[Tuple[Oid, Module]]:
        return self.metrics


class NestingVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[Tuple[Oid, int]] = []

    def visitBlob(self, blob: VisitableBlob) -> NestingVisitor:
        if blob.obj.name.endswith(".py"):
            m = parse(blob.obj.data)
            self.metrics.append((blob.obj.id, NestingASTVisitor().visit(m).result))
        return self

    @property
    def result(self) -> List[Tuple[Oid, int]]:
        return self.metrics
