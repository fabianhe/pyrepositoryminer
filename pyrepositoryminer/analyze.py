from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, TypedDict

from pygit2 import Commit, Repository, Tree

from pyrepositoryminer.helper import (
    BlobOutput,
    CommitOutput,
    Metric,
    UnitOutput,
    parse_commit,
)
from pyrepositoryminer.metrics import BlobMetrics, TreeMetrics, UnitMetrics
from pyrepositoryminer.visitableobject import VisitableTree

repo: Repository

tm: Tuple[str, ...]
bm: Tuple[str, ...]
um: Tuple[str, ...]


BlobEntry = TypedDict(
    "BlobEntry", {"metrics": List[Metric], "units": Dict[str, List[Metric]]}
)


def validate_commit(repository: Repository, commit_id: str) -> bool:
    try:
        obj = repository.get(commit_id)
    except ValueError:
        return False
    else:
        return obj is not None and isinstance(obj, Commit)


def initialize(
    repository: Path,
    tree_m: Iterable[str],
    blob_m: Iterable[str],
    unit_m: Iterable[str],
) -> None:
    global repo
    repo = Repository(repository)
    global tm
    tm = tuple(sorted(tree_m))
    global bm
    bm = tuple(sorted(blob_m))
    global um
    um = tuple(sorted(unit_m))


def analyze_unit(tree: Tree) -> Iterable[Tuple[str, str, Metric]]:
    global um
    for m in um:
        for res in UnitMetrics[m]().visitTree(VisitableTree(tree)).result:
            yield str(res.blob_id), str(res.unit_id), Metric(name=m, value=res.value)


def analyze_blob(tree: Tree) -> Iterable[Tuple[str, Metric]]:
    global bm
    for m in bm:
        for res in BlobMetrics[m]().visitTree(VisitableTree(tree)).result:
            yield str(res.blob_id), Metric(name=m, value=res.value)


def analyze_tree(tree: Tree) -> Iterable[Metric]:
    global tm
    for m in tm:
        yield Metric(
            name=m,
            value=TreeMetrics[m]().visitTree(VisitableTree(tree)).result.value,
        )


def analyze(commit_id: str) -> Optional[CommitOutput]:
    global repo
    try:
        commit = repo.get(commit_id)
    except ValueError:
        return None
    else:
        if commit is None or not isinstance(commit, Commit):
            return None

    d: Dict[str, BlobEntry] = {}
    for blob_id, unit_id, metric in analyze_unit(commit.tree):
        d.setdefault(blob_id, {"metrics": [], "units": {}})["units"].setdefault(
            unit_id, []
        ).append(metric)
    for blob_id, metric in analyze_blob(commit.tree):
        d.setdefault(blob_id, {"metrics": [], "units": {}})["metrics"].append(metric)
    return parse_commit(
        commit,
        metrics=analyze_tree(commit.tree),
        blobs=[
            BlobOutput(
                id=str(blob_id),
                metrics=blob["metrics"],
                units=[
                    UnitOutput(id=unit_id, metrics=unit)
                    for unit_id, unit in blob["units"].items()
                ],
            )
            for blob_id, blob in d.items()
        ],
    )
