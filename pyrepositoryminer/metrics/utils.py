from functools import reduce
from typing import FrozenSet

from pygit2._pygit2 import DiffFile

from pyrepositoryminer.pobjects import Commit, Tree


def get_touchedfiles(commit: Commit) -> FrozenSet[DiffFile]:
    if not commit.parents:
        return frozenset(
            delta.new_file for delta in commit.tree.obj.diff_to_tree(swap=True).deltas
        )
    return frozenset(
        delta.new_file
        for parent in commit.parents
        for delta in commit.tree.obj.diff_to_tree(parent.tree.obj, swap=True).deltas
        if delta.status_char() != "D"
    )


def descend_tree(tree: Tree, obj_name: str) -> str:
    return reduce(lambda a, b: a[b], obj_name.split("/"), tree).id  # type: ignore
