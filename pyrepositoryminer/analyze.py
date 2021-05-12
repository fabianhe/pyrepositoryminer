from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Iterable, List, Optional, Tuple, TypedDict

from pygit2 import Commit, Repository

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


class blobhelper(TypedDict):
    metrics: List[Metric]
    units: DefaultDict[str, List[Metric]]


blobshelper = DefaultDict[str, blobhelper]


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


def analyze(commit_id: str) -> Optional[CommitOutput]:
    global repo
    try:
        commit = repo.get(commit_id)
    except ValueError:
        return None
    else:
        if commit is None or not isinstance(commit, Commit):
            return None

    blobs: blobshelper = defaultdict(
        lambda: {"metrics": [], "units": defaultdict(list)}
    )

    global um
    for m in um:
        for res in UnitMetrics[m]().visitTree(VisitableTree(commit.tree)).result:
            blobs[res.blob_id]["units"][res.unit_id].append(
                Metric(name=m, value=res.value)
            )

    global bm
    for m in bm:
        for res in BlobMetrics[m]().visitTree(VisitableTree(commit.tree)).result:
            blobs[res.blob_id]["metrics"].append(Metric(name=m, value=res.value))

    global tm
    return parse_commit(
        commit,
        metrics=[
            Metric(
                name=m,
                value=TreeMetrics[m]()
                .visitTree(VisitableTree(commit.tree))
                .result.value,
            )
            for m in tm
        ],
        blobs=[
            BlobOutput(
                id=str(blob_id),
                metrics=blob["metrics"],
                units=[
                    UnitOutput(id=unit_id, metrics=unit)
                    for unit_id, unit in blob["units"].items()
                ],
            )
            for blob_id, blob in blobs.items()
        ],
    )
