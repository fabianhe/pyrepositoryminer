from abc import ABC, abstractmethod
from typing import Iterable

from pygit2 import Repository

from pyrepositoryminer.metrics.main import BaseMetric, BaseVisitor
from pyrepositoryminer.metrics.structs import NativeBlobMetricInput
from pyrepositoryminer.metrics.utils import get_touchedfiles
from pyrepositoryminer.pobjects import Blob, Commit, Object


class DiffBlobVisitor(BaseVisitor):
    def __init__(self, repository: Repository) -> None:
        super().__init__()
        self.repository = repository

    def __call__(self, visitable_object: Object) -> Iterable[NativeBlobMetricInput]:
        if isinstance(visitable_object, Commit):
            for file in get_touchedfiles(visitable_object):
                blob = Blob(self.repository.get(file.id))
                yield NativeBlobMetricInput(
                    self.oid_is_cached(blob.id), str(file.path), blob
                )
                self.cache_oid(blob.id)


class DiffBlobMetric(BaseMetric[NativeBlobMetricInput], ABC):
    @staticmethod
    @abstractmethod
    def filter(tup: NativeBlobMetricInput) -> bool:
        pass
