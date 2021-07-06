from abc import ABC, abstractmethod
from typing import Awaitable, Generic, Iterable, TypeVar, final

from pyrepositoryminer.metrics.structs import BaseMetricInput, Metric

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
        else:
            return await self.analyze(tup)

    @classmethod
    @property
    def name(cls) -> str:
        return str(cls.__name__).lower()
