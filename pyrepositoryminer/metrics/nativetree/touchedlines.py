from typing import Iterable

from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric
from pyrepositoryminer.metrics.structs import Metric, TreeTuple

# optionally filter the files with
# patch.delta.old_file or patch.delta.new_file
# https://www.pygit2.org/diff.html#the-diffdelta-type

# optionally filter "+", "-" or " " with line.origin
# https://www.pygit2.org/diff.html#the-diffline-type


class TouchedLines(NativeTreeMetric):
    async def analyze(self, tree_tup: TreeTuple) -> Iterable[Metric]:
        touched_lines = ""
        for parent in tree_tup.commit.parents:
            diff = tree_tup.tree.obj.diff_to_tree(parent.tree.obj)
            for patch in diff:
                for hunk in patch.hunks:
                    for line in hunk.lines:
                        touched_lines += line.content
        return [Metric(self.name, touched_lines, False)]
