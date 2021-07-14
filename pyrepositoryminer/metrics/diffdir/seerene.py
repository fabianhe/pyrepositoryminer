from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from csv import DictReader
from functools import reduce
from io import TextIOWrapper
from json import dump
from os import getenv
from pathlib import Path
from tempfile import NamedTemporaryFile
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
        if (executables := getenv("EXECUTABLES")) is None or (
            token := getenv("LOCALANALYZER_TOKEN")
        ) is None:
            return []
        localanalyzer = (Path(executables) / "localanalyzer-v2.16").resolve()
        p = await create_subprocess_exec(
            localanalyzer, "init", "--token", token, cwd=dir_tup.path, stdout=PIPE
        )
        await p.communicate()
        f = NamedTemporaryFile("w")
        log = NamedTemporaryFile("w")
        dump(
            {
                "author-anonymization": False,
                "components": {
                    "code-log-export": {
                        ".": {
                            "export-codedir-path": ".",
                            "export-logfile-path": log.name,
                            "prefix": "",
                            "vcs-type": "git",
                        }
                    }
                },
                "type": "seerene-application-import-configuration",
                "version": "1",
            },
            f,
            sort_keys=True,
            indent=4,
        )
        f.seek(0)
        p = await create_subprocess_exec(
            localanalyzer, "import", f.name, cwd=dir_tup.path, stdout=PIPE
        )
        await p.communicate()
        f.close()
        p = await create_subprocess_exec(
            localanalyzer, "analyze", cwd=dir_tup.path, stdout=PIPE
        )
        await p.communicate()
        log.close()
        result = []
        with ZipFile(list((Path(dir_tup.path) / "pending").glob("*.zip"))[0]) as myzip:
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
