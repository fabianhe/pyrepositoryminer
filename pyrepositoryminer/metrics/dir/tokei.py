from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from typing import Iterable

from pyrepositoryminer.metrics.dir.main import DirMetric
from pyrepositoryminer.metrics.structs import DirTuple, Metric


class Tokei(DirMetric):
    async def analyze(self, dir_tup: DirTuple) -> Iterable[Metric]:
        p = await create_subprocess_exec(
            "tokei", "--output", "json", dir_tup.path, stdout=PIPE
        )
        stdout, _ = await p.communicate()
        return [Metric(self.name, bytes(stdout).decode("utf-8"), False)]
