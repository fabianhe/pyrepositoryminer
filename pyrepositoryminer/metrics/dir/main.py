from abc import ABC
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pygit2 import Repository

from pyrepositoryminer.metrics.main import BaseMetric
from pyrepositoryminer.metrics.structs import DirMetricInput
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

    async def __call__(
        self, visitable_object: VisitableObject
    ) -> Optional[DirMetricInput]:
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
        return DirMetricInput(False, path, self.commit.tree)

    async def close(self) -> None:
        self.worktree.prune(True)
        self.ref.delete()
        self.tempdir.cleanup()


class DirMetric(BaseMetric[DirMetricInput], ABC):
    pass
