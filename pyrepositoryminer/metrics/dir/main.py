from abc import ABC, abstractmethod
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Any, Awaitable, Iterable, Optional, final

from pygit2 import Repository

from pyrepositoryminer.metrics.structs import DirTuple, Metric
from pyrepositoryminer.metrics.visitor import TreeVisitor
from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableCommit,
    VisitableObject,
    VisitableTree,
)


class DirVisitor(TreeVisitor):
    def __init__(self, repository: Repository) -> None:
        super().__init__()
        self.repository = repository

    async def visitCommit(self, commit: VisitableCommit) -> None:
        if self.visited_commit:
            return
        self.visited_commit = True
        self.commit: Optional[VisitableCommit] = commit
        self.cache_oid(commit.id)

    async def visitTree(self, tree: VisitableTree) -> None:
        pass

    async def visitBlob(self, blob: VisitableBlob) -> None:
        pass

    async def __call__(self, visitable_object: VisitableObject) -> Optional[DirTuple]:
        self.visited_commit = False
        self.commit = None
        await visitable_object.accept(self)
        if self.commit is None:
            return None
        self.ref: Any = self.repository.references.create(
            f"refs/heads/{datetime.now().timestamp()}", self.commit.id
        )
        self.tempdir: TemporaryDirectory[str] = TemporaryDirectory()
        self.wtname = f"wt_{self.commit.id}"
        path = f"{self.tempdir.name}/{self.wtname}"
        self.worktree: Any = self.repository.add_worktree(self.wtname, path, self.ref)
        return DirTuple(path=path, is_cached=False)

    async def close(self) -> None:
        self.worktree.prune(True)
        self.ref.delete()
        self.tempdir.cleanup()


class DirMetric(ABC):
    async def cache_hit(self, dir_tup: DirTuple) -> Iterable[Metric]:
        return await self.analyze(dir_tup)

    @abstractmethod
    def analyze(self, dir_tup: DirTuple) -> Awaitable[Iterable[Metric]]:
        pass

    @final
    async def __call__(self, dir_tup: DirTuple) -> Iterable[Metric]:
        if dir_tup.is_cached:
            return await self.cache_hit(dir_tup)
        else:
            return await self.analyze(dir_tup)

    @classmethod
    @property
    def name(cls) -> str:
        return str(cls.__name__).lower()
