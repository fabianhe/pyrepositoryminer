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
from dataclasses import dataclass
from typing import Any, Iterable, List

from pygit2 import Blob, Oid, Tree
from radon.complexity import cc_visit
from radon.raw import Module, analyze

from .visitableobject import VisitableBlob, VisitableTree


@dataclass(frozen=True)
class TreeMetricOutput:
    value: Any


@dataclass(frozen=True)
class BlobMetricOutput(TreeMetricOutput):
    blob_id: Oid


@dataclass(frozen=True)
class UnitMetricOutput(BlobMetricOutput):
    unit_id: str


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


class TreeMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> TreeMetricOutput:
        pass


class BlobMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> Iterable[BlobMetricOutput]:
        pass


class UnitMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> Iterable[UnitMetricOutput]:
        pass


class LocVisitor(TreeMetric):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> LocVisitor:
        self.n += 0 if blob.obj.is_binary else len(blob.obj.data.split(b"\n"))
        return self

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)


class FilecountVisitor(TreeMetric):
    def __init__(self) -> None:
        super().__init__()
        self.n: int = 0

    def visitBlob(self, blob: VisitableBlob) -> FilecountVisitor:
        self.n += 1
        return self

    @property
    def result(self) -> TreeMetricOutput:
        return TreeMetricOutput(value=self.n)


class ComplexityVisitor(UnitMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[UnitMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> ComplexityVisitor:
        if blob.obj.name.endswith(".py"):
            if complexities := cc_visit(blob.obj.data):
                self.metrics.extend(
                    UnitMetricOutput(
                        unit_id=str(u.fullname),
                        value=int(u.complexity),
                        blob_id=blob.obj.id,
                    )
                    for u in complexities
                )

        return self

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        return self.metrics


class RawVisitor(BlobMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> RawVisitor:
        if blob.obj.name.endswith(".py"):
            data: Module = analyze(blob.obj.data.decode())
            self.metrics.append(
                BlobMetricOutput(
                    value=data._asdict(),
                    blob_id=blob.obj.id,
                )
            )

        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics


class NestingVisitor(BlobMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[BlobMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> NestingVisitor:
        if blob.obj.name.endswith(".py"):
            m = parse(blob.obj.data)
            self.metrics.append(
                BlobMetricOutput(
                    value=NestingASTVisitor().visit(m).result,
                    blob_id=blob.obj.id,
                )
            )
        return self

    @property
    def result(self) -> Iterable[BlobMetricOutput]:
        return self.metrics


class LineLengthVisitor(UnitMetric):
    def __init__(self) -> None:
        super().__init__()
        self.metrics: List[UnitMetricOutput] = []

    def visitBlob(self, blob: VisitableBlob) -> LineLengthVisitor:
        if blob.obj.is_binary:
            return self
        for i, line in enumerate(blob.obj.data.split(b"\n")):
            self.metrics.append(
                UnitMetricOutput(len(line), blob_id=blob.obj.id, unit_id=f"L{i+1}")
            )
        return self

    @property
    def result(self) -> Iterable[UnitMetricOutput]:
        return self.metrics
