from typing import Iterable

from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric
from pyrepositoryminer.metrics.structs import Metric, NativeTreeMetricInput

# optionally filter the files with
# patch.delta.old_file or patch.delta.new_file
# https://www.pygit2.org/diff.html#the-diffdelta-type

# optionally filter "+", "-" or " " with line.origin
# https://www.pygit2.org/diff.html#the-diffline-type


class TouchedLines(NativeTreeMetric):
    async def analyze(self, tup: NativeTreeMetricInput) -> Iterable[Metric]:
        parent_trees = tuple(parent.tree.obj for parent in tup.commit.parents)
        if not parent_trees:  # orphan commit is diffed to empty tree
            diffs = [tup.tree.obj.diff_to_tree(swap=True)]

        else:
            diffs = [
                tup.tree.obj.diff_to_tree(parent_tree, swap=True)
                for parent_tree in parent_trees
            ]
        touched_lines = [
            line.content
            for diff in diffs
            for patch in diff
            for hunk in patch.hunks
            for line in hunk.lines
            if line.content_offset > -1
        ]
        return [Metric(self.name, touched_lines, False)]
