from abc import ABC, abstractmethod
from typing import Any, Awaitable, Generic, Iterable, Set, TypeVar, final

from pyrepositoryminer.metrics.structs import BaseMetricInput, Metric
from pyrepositoryminer.pobjects import Object


class BaseVisitor(ABC):
    def __init__(self) -> None:
        self.oid_cache: Set[str] = set()

    def oid_is_cached(self, oid: str) -> bool:
        return oid in self.oid_cache

    def cache_oid(self, oid: str) -> None:
        self.oid_cache.add(oid)

    @abstractmethod
    def __call__(self, visitable_object: Object) -> Any:
        pass


T = TypeVar("T", bound=BaseMetricInput)


class BaseMetric(Generic[T], ABC):
    async def cache_hit(self, tup: T) -> Iterable[Metric]:
        return await self.analyze(tup)

    @abstractmethod
    def analyze(self, tup: T) -> Awaitable[Iterable[Metric]]:
        ...

    @final
    async def __call__(self, tup: T) -> Iterable[Metric]:
        if tup.is_cached:
            return await self.cache_hit(tup)
        return await self.analyze(tup)

    @classmethod
    @property
    def name(cls) -> str:
        return str(cls.__name__).lower()
