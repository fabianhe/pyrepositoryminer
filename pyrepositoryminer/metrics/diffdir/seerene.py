from asyncio import create_subprocess_exec
from csv import DictReader
from functools import reduce
from io import TextIOWrapper
from typing import Iterable
from zipfile import ZipFile

from pyrepositoryminer.metrics.diffdir.main import DiffDirMetric
from pyrepositoryminer.metrics.structs import DirMetricInput, Metric, ObjectIdentifier
from pyrepositoryminer.pobjects import Tree


def descend_tree(tree: Tree, obj_name: str) -> str:
    return reduce(lambda a, b: a[b], obj_name.split("/"), tree).id  # type: ignore


class Seerene(DiffDirMetric):
    async def analyze(self, dir_tup: DirMetricInput) -> Iterable[Metric]:
        # assuming 'init' and 'import' have been called
        p = await create_subprocess_exec(
            "$SEERENE_EXECUTABLE", "analyze", cwd=dir_tup.path
        )
        await p.communicate()
        result = []
        with ZipFile("$SEERENE_EXECUTABLE/pending") as myzip:
            with TextIOWrapper(myzip.open("m_main.csv")) as f:
                reader = DictReader(f, delimiter=";")
                for row in reader:
                    path = row.pop("filename")
                    result.append(
                        Metric(
                            self.name,
                            row,
                            False,
                            ObjectIdentifier(descend_tree(dir_tup.tree, path), path),
                        )
                    )
        return result
