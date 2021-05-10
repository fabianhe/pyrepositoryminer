from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pyrepositoryminer.metrics.visitor import TreeVisitor


@dataclass(frozen=True)
class TreeMetricOutput:
    value: Any


class TreeMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> TreeMetricOutput:
        pass
