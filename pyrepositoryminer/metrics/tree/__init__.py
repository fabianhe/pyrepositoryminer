from abc import ABC, abstractmethod
from typing import Any, TypedDict

from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import VisitableBlob


class MetricBase(TypedDict):
    value: Any


class TreeMetricOutput(MetricBase, total=False):
    cached: bool


class TreeMetric(TreeVisitor, ABC):
    def handle_cache_hit(self, blob: VisitableBlob) -> None:
        pass

    @property
    @abstractmethod
    def result(self) -> TreeMetricOutput:
        pass
