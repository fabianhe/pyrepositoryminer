from abc import ABC, abstractmethod
from asyncio import as_completed
from typing import AsyncIterable, Awaitable, Callable, Iterable, List, Set, final

from pyrepositoryminer.metrics.structs import BlobTuple, Metric
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableObject,
    VisitableTree,
)


class NativeBlobVisitor(TreeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.blobs: List[BlobTuple] = []

    async def visitTree(self, tree: VisitableTree) -> None:
        for visitable_object in tree:
            self.path.append(visitable_object.name)
            await visitable_object.accept(self)
            self.path.pop(-1)

    async def visitBlob(self, blob: VisitableBlob) -> None:
        self.blobs.append(BlobTuple(self.pathname, blob, self.oid_is_cached(blob.id)))
        self.cache_oid(blob.id)

    async def __call__(
        self, visitable_object: VisitableObject
    ) -> AsyncIterable[BlobTuple]:
        await visitable_object.accept(self)
        for blob in self.blobs:
            yield blob


class NativeBlobFilter:
    def __init__(self, *filters: Callable[[BlobTuple], Awaitable[bool]]) -> None:
        self.filters = filters
        self.cached_oids: Set[str] = set()

    async def __call__(self, tup: BlobTuple) -> AsyncIterable[BlobTuple]:
        if tup.is_cached and (tup.blob.id not in self.cached_oids):
            yield tup  # cached but not filtered
        elif not tup.is_cached:
            for val in as_completed(tuple(filter(tup) for filter in self.filters)):
                if await val:
                    self.cached_oids.add(tup.blob.id)  # now cached and filtered
                    break
            else:
                yield tup  # neither cached nor filtered

    @staticmethod
    def endswith(ending: str) -> Callable[[BlobTuple], Awaitable[bool]]:
        async def filter(tup: BlobTuple) -> bool:
            return not tup.blob.name.endswith(ending)

        return filter

    @staticmethod
    def is_binary() -> Callable[[BlobTuple], Awaitable[bool]]:
        async def filter(tup: BlobTuple) -> bool:
            return tup.blob.is_binary

        return filter


class NativeBlobMetric(ABC):
    name: str
    filter: NativeBlobFilter

    async def cache_hit(self, blob_tup: BlobTuple) -> Iterable[Metric]:
        return await self.analyze(blob_tup)

    @abstractmethod
    def analyze(self, blob_tup: BlobTuple) -> Awaitable[Iterable[Metric]]:
        pass

    @final
    async def __call__(self, tup: BlobTuple) -> Iterable[Metric]:
        if tup.is_cached:
            return await self.cache_hit(tup)
        else:
            return await self.analyze(tup)
