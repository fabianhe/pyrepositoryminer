from abc import ABC
from tempfile import TemporaryDirectory
from typing import FrozenSet, Optional

from pygit2 import GIT_CHECKOUT_FORCE, Repository
from pygit2._pygit2 import DiffFile

from pyrepositoryminer.metrics.main import BaseMetric, BaseVisitor
from pyrepositoryminer.metrics.structs import DirMetricInput
from pyrepositoryminer.pobjects import Commit, Object


def get_touchedfiles(commit: Commit) -> FrozenSet[DiffFile]:
    if not commit.parents:
        return frozenset(
            delta.new_file for delta in commit.tree.obj.diff_to_tree(swap=True).deltas
        )
    return frozenset(
        delta.new_file
        for parent in commit.parents
        for delta in commit.tree.obj.diff_to_tree(parent.tree.obj, swap=True).deltas
    )


class DiffDirVisitor(BaseVisitor):
    def __init__(self, repository: Repository, base_dir: Optional[str] = None) -> None:
        super().__init__()
        self.repository = repository
        self.base_dir = base_dir

    def __call__(self, visitable_object: Object) -> Optional[DirMetricInput]:
        if not isinstance(visitable_object, Commit):
            return None
        self.tempdir: TemporaryDirectory[str] = TemporaryDirectory(dir=self.base_dir)
        self.repository.checkout_tree(
            visitable_object.tree.obj,
            directory=self.tempdir.name,
            paths=[file.path for file in get_touchedfiles(visitable_object)],
            strategy=GIT_CHECKOUT_FORCE,
        )
        is_cached = self.oid_is_cached(visitable_object.tree.id)
        self.cache_oid(visitable_object.tree.id)
        return DirMetricInput(is_cached, self.tempdir.name, visitable_object.tree)

    def close(self) -> None:
        self.tempdir.cleanup()


class DiffDirMetric(BaseMetric[DirMetricInput], ABC):
    pass
