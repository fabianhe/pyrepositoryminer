from abc import ABC, abstractmethod
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Awaitable, Iterable, Optional, final

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

    async def __call__(self, visitable_object: VisitableObject) -> None:
        self.visited_commit = False
        self.commit = None
        await visitable_object.accept(self)

    async def __aenter__(self) -> "DirVisitor":
        if self.commit is None:
            self.dir_tup: Optional[DirTuple] = None
            return self
        self.ref = self.repository.references.create(
            f"refs/heads/{datetime.now().timestamp()}", self.commit.id
        )
        self.tempdir = TemporaryDirectory()
        self.wtname = f"wt_{self.commit.id}"
        path = f"{self.tempdir.name}/{self.wtname}"
        self.worktree = self.repository.add_worktree(self.wtname, path, self.ref)
        self.dir_tup = DirTuple(path=path, is_cached=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
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
