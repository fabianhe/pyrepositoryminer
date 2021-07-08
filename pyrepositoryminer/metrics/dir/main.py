from abc import ABC
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Any, Optional

from pygit2 import Repository

from pyrepositoryminer.metrics.main import BaseMetric, BaseVisitor
from pyrepositoryminer.metrics.structs import DirMetricInput
from pyrepositoryminer.pobjects import Commit, Object


class DirVisitor(BaseVisitor):
    def __init__(self, repository: Repository, base_dir: Optional[str] = None) -> None:
        super().__init__()
        self.repository = repository
        self.base_dir = base_dir

    def __call__(self, visitable_object: Object) -> Optional[DirMetricInput]:
        if not isinstance(visitable_object, Commit):
            return None
        refname = f"refs/heads/{datetime.now().timestamp()}_{visitable_object.id}"
        self.ref: Any = self.repository.references.create(refname, visitable_object.id)
        self.tempdir: TemporaryDirectory[str] = TemporaryDirectory()
        self.wtname = f"wt_{visitable_object.id}"
        path = f"{self.tempdir.name}/{self.wtname}"
        self.worktree: Any = self.repository.add_worktree(self.wtname, path, self.ref)
        is_cached = self.oid_is_cached(visitable_object.tree.id)
        self.cache_oid(visitable_object.tree.id)
        return DirMetricInput(is_cached, path, visitable_object.tree)

    def close(self) -> None:
        self.worktree.prune(True)
        self.ref.delete()
        self.tempdir.cleanup()


class DirMetric(BaseMetric[DirMetricInput], ABC):
    pass
