from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from pyrepositoryminer.metrics.blob import BlobMetricOutput
from pyrepositoryminer.metrics.visitor import TreeVisitor


@dataclass(frozen=True)
class UnitMetricOutput(BlobMetricOutput):
    unit_id: str


class UnitMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> Iterable[UnitMetricOutput]:
        pass
