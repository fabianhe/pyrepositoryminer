from __future__ import annotations

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
from typing import Iterable

from pyrepositoryminer.metrics.nativeblob.main import NativeBlobFilter, NativeBlobMetric
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)


class Nesting(NativeBlobMetric):
    filter = NativeBlobFilter(NativeBlobFilter.endswith(".py"))

    async def analyze(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        result = [
            Metric(
                self.name,
                NestingASTVisitor().visit(parse(tup.blob.obj.data)).result,
                False,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        ]
        return result


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
