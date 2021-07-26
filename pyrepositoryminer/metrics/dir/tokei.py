from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from json import loads
from typing import Iterable

from pyrepositoryminer.metrics.dir.main import DirMetric
from pyrepositoryminer.metrics.structs import DirMetricInput, Metric, ObjectIdentifier
from pyrepositoryminer.metrics.utils import descend_tree
from pyrepositoryminer.pobjects import Tree


async def tokei(name: str, path: str, tree: Tree) -> Iterable[Metric]:
    p = await create_subprocess_exec("tokei", "--output", "json", path, stdout=PIPE)
    stdout, _ = await p.communicate()
    data = loads(bytes(stdout).decode("utf-8"))
    result = [
        Metric(
            name,
            {
                "category": category_name,
                "blanks": report["stats"]["blanks"],
                "code": report["stats"]["code"],
                "comments": report["stats"]["comments"],
            },
            False,
            ObjectIdentifier(
                descend_tree(tree, report["name"][len(path) + 1 :]),
                report["name"][len(path) + 1 :],
            ),
        )
        for category_name, reports in data["Total"]["children"].items()
        for report in reports
    ]
    result.append(
        Metric(
            name,
            {
                "blanks": data["Total"]["blanks"],
                "code": data["Total"]["code"],
                "comments": data["Total"]["comments"],
            },
            False,
        )
    )
    return result


class Tokei(DirMetric):
    async def analyze(self, tup: DirMetricInput) -> Iterable[Metric]:
        return await tokei(self.name, tup.path, tup.tree)
