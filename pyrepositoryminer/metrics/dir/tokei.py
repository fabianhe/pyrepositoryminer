from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from json import loads
from typing import Iterable

from pyrepositoryminer.metrics.dir.main import DirMetric
from pyrepositoryminer.metrics.structs import DirMetricInput, Metric, ObjectIdentifier
from pyrepositoryminer.metrics.utils import descend_tree


class Tokei(DirMetric):
    async def analyze(self, tup: DirMetricInput) -> Iterable[Metric]:
        p = await create_subprocess_exec(
            "tokei", "--output", "json", tup.path, stdout=PIPE
        )
        stdout, _ = await p.communicate()
        data = loads(bytes(stdout).decode("utf-8"))
        result = [
            Metric(
                self.name,
                {
                    "category": category_name,
                    "blanks": report["stats"]["blanks"],
                    "code": report["stats"]["code"],
                    "comments": report["stats"]["comments"],
                },
                False,
                ObjectIdentifier(
                    descend_tree(tup.tree, report["name"][len(tup.path) + 1 :]),
                    report["name"][len(tup.path) + 1 :],
                ),
            )
            for category_name, reports in data["Total"]["children"].items()
            for report in reports
        ]
        result.append(
            Metric(
                self.name,
                {
                    "blanks": data["Total"]["blanks"],
                    "code": data["Total"]["code"],
                    "comments": data["Total"]["comments"],
                },
                False,
            )
        )
        return result
