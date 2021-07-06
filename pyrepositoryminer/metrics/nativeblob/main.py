from abc import ABC, abstractmethod
from asyncio import as_completed
from typing import AsyncIterable, Awaitable, Callable, List, Set

from pyrepositoryminer.metrics.main import BaseMetric
from pyrepositoryminer.metrics.structs import NativeBlobMetricInput
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableObject,
    VisitableTree,
)


class NativeBlobVisitor(TreeVisitor):
    async def visitTree(self, tree: VisitableTree) -> None:
        for visitable_object in tree:
            self.path.append(visitable_object.name)
            await visitable_object.accept(self)
            self.path.pop(-1)

    async def visitBlob(self, blob: VisitableBlob) -> None:
        self.blobs.append(
            NativeBlobMetricInput(self.oid_is_cached(blob.id), self.pathname, blob)
        )
        self.cache_oid(blob.id)

    async def __call__(
        self, visitable_object: VisitableObject
    ) -> AsyncIterable[NativeBlobMetricInput]:
        self.visited_commit = False
        self.blobs: List[NativeBlobMetricInput] = []
        await visitable_object.accept(self)
        for blob in self.blobs:
            yield blob


class NativeBlobFilter:
    def __init__(
        self, *filters: Callable[[NativeBlobMetricInput], Awaitable[bool]]
    ) -> None:
        self.filters = filters
        self.cached_oids: Set[str] = set()

    async def __call__(self, tup: NativeBlobMetricInput) -> bool:
        if tup.is_cached:
            if tup.blob.id in self.cached_oids:
                return True
        else:
            for val in as_completed(tuple(filter(tup) for filter in self.filters)):
                if await val:
                    self.cached_oids.add(tup.blob.id)
                    return True
        return False

    @staticmethod
    def endswith(ending: str) -> Callable[[NativeBlobMetricInput], Awaitable[bool]]:
        async def filter(tup: NativeBlobMetricInput) -> bool:
            return not tup.blob.name.endswith(ending)

        return filter

    @staticmethod
    def is_binary() -> Callable[[NativeBlobMetricInput], Awaitable[bool]]:
        async def filter(tup: NativeBlobMetricInput) -> bool:
            return tup.blob.is_binary

        return filter


class NativeBlobMetric(BaseMetric[NativeBlobMetricInput], ABC):
    @staticmethod
    @abstractmethod
    def filter(tup: NativeBlobMetricInput) -> Awaitable[bool]:
        pass
