from abc import ABC, abstractmethod
from typing import Callable, Iterable, List, Set, Tuple

from pyrepositoryminer.metrics.main import BaseMetric, BaseVisitor
from pyrepositoryminer.metrics.structs import (
    Metric,
    NativeBlobMetricInput,
    ObjectIdentifier,
)
from pyrepositoryminer.pobjects import Blob, Commit, Object, Tree


class NativeBlobVisitor(BaseVisitor):
    def __call__(self, visitable_object: Object) -> Iterable[NativeBlobMetricInput]:
        if isinstance(visitable_object, Commit):
            visited_commit = False
            q: List[Tuple[Object, str]] = [(visitable_object, "")]
            while q:
                vo, path = q.pop(0)
                if isinstance(vo, Blob):
                    yield NativeBlobMetricInput(
                        self.oid_is_cached(vo.id), f"{path}/{vo.name}", vo
                    )
                elif isinstance(vo, Tree):
                    p = f"{f'{path}/' if path else ''}{vo.name if vo.name else ''}"
                    q.extend((sub_vo, p) for sub_vo in vo)
                elif isinstance(vo, Commit) and not visited_commit:
                    q.append((vo.tree, ""))
                    visited_commit = True
                self.cache_oid(vo.id)


class NativeBlobFilter:
    def __init__(self, *filters: Callable[[NativeBlobMetricInput], bool]) -> None:
        self.filters = filters
        self.cached_oids: Set[str] = set()

    def __call__(self, tup: NativeBlobMetricInput) -> bool:
        if tup.is_cached:
            if tup.blob.id in self.cached_oids:
                return True
        else:
            if any(f(tup) for f in self.filters):
                self.cached_oids.add(tup.blob.id)
                return True
        return False

    @staticmethod
    def endswith(ending: str) -> Callable[[NativeBlobMetricInput], bool]:
        def f(tup: NativeBlobMetricInput) -> bool:
            return not tup.blob.name.endswith(ending)

        return f

    @staticmethod
    def is_binary() -> Callable[[NativeBlobMetricInput], bool]:
        def f(tup: NativeBlobMetricInput) -> bool:
            return bool(tup.blob.is_binary)

        return f


class NativeBlobMetric(BaseMetric[NativeBlobMetricInput], ABC):
    async def cache_hit(self, tup: NativeBlobMetricInput) -> Iterable[Metric]:
        return [
            Metric(
                self.name,
                None,
                True,
                ObjectIdentifier(tup.blob.id, tup.path),
            )
        ]

    @staticmethod
    @abstractmethod
    def filter(tup: NativeBlobMetricInput) -> bool:
        pass
