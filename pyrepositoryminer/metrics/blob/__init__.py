from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from pyrepositoryminer.metrics.tree import TreeMetricOutput
from pyrepositoryminer.metrics.visitor import TreeVisitor


@dataclass(frozen=True)
class BlobMetricOutput(TreeMetricOutput):
    blob_id: str
    blob_name: str


class BlobMetric(TreeVisitor, ABC):
    @property
    @abstractmethod
    def result(self) -> Iterable[BlobMetricOutput]:
        pass
