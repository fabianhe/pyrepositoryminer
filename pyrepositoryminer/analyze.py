"""Analyze a commit w.r.t tree-, blob- or unit-metrics.

Global variables are accessed in the context of a worker.
"""
from json import dumps
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, TypedDict

from pygit2 import Commit, Repository, Signature, Tree

from pyrepositoryminer.metrics import BlobMetrics, TreeMetrics, UnitMetrics
from pyrepositoryminer.visitableobject import VisitableTree

repo: Repository

tm: Tuple[str, ...]
bm: Tuple[str, ...]
um: Tuple[str, ...]
cached_oids: Dict[str, bool] = {}


class MetricBase(TypedDict):
    name: str


class Metric(MetricBase, total=False):
    value: Any
    cached: bool


class ObjectOutput(TypedDict):
    id: str


class UnitOutput(ObjectOutput):
    metrics: List[Metric]


class BlobOutput(ObjectOutput):
    name: str
    metrics: List[Metric]
    units: List[UnitOutput]


SignatureOutput = TypedDict(
    "SignatureOutput", {"email": str, "name": str, "time_offset": int, "time": int}
)


class CommitOutput(ObjectOutput):
    author: SignatureOutput
    commit_time: int
    commit_time_offset: int
    committer: SignatureOutput
    message: str
    parent_ids: List[str]
    metrics: List[Metric]
    blobs: List[BlobOutput]


BlobEntry = TypedDict(
    "BlobEntry",
    {"name": str, "metrics": List[Metric], "units": Dict[str, List[Metric]]},
)


def parse_commit(
    commit: Commit,
    metrics: Iterable[Metric],
    blobs: Iterable[BlobOutput],
) -> CommitOutput:
    def parse_signature(signature: Signature) -> SignatureOutput:
        return SignatureOutput(
            email=str(signature.email),
            name=str(signature.name),
            time_offset=int(signature.offset),
            time=int(signature.time),
        )

    return CommitOutput(
        id=str(commit.id),
        author=parse_signature(commit.author),
        commit_time=int(commit.commit_time),
        commit_time_offset=int(commit.commit_time_offset),
        committer=parse_signature(commit.committer),
        message=str(commit.message),
        parent_ids=[str(id) for id in commit.parent_ids],
        metrics=list(metrics),
        blobs=list(blobs),
    )


def initialize(
    repository: Path,
    tree_m: Tuple[str, ...],
    blob_m: Tuple[str, ...],
    unit_m: Tuple[str, ...],
) -> None:
    global repo, tm, bm, um
    repo = Repository(repository)
    tm = tree_m
    bm = blob_m
    um = unit_m


def analyze_unit(tree: Tree) -> Iterable[Tuple[str, str, str, Metric]]:
    global um, cached_oids
    for m in um:
        for res in UnitMetrics[m](cached_oids).visitTree(VisitableTree(tree)).result:
            metric = Metric(name=m)
            if res.get("cached", False):
                metric["cached"] = True
            else:
                metric["value"] = res["value"]
            yield str(res["blob_id"]), str(res["blob_name"]), str(
                res["unit_id"]
            ), metric


def analyze_blob(tree: Tree) -> Iterable[Tuple[str, str, Metric]]:
    global bm, cached_oids
    for m in bm:
        for res in BlobMetrics[m](cached_oids).visitTree(VisitableTree(tree)).result:
            metric = Metric(name=m)
            if res.get("cached", False):
                metric["cached"] = True
            else:
                metric["value"] = res["value"]
            yield str(res["blob_id"]), str(res["blob_name"]), metric


def analyze_tree(tree: Tree) -> Iterable[Metric]:
    global tm, cached_oids
    for m in tm:
        res = TreeMetrics[m](cached_oids).visitTree(VisitableTree(tree)).result
        metric = Metric(name=m)
        if res.get("cached", False):
            metric["cached"] = True
        else:
            metric["value"] = res["value"]
        yield metric


def analyze(commit_id: str) -> Optional[str]:
    global repo
    try:
        commit = repo.get(commit_id)
    except ValueError:
        return None
    else:
        if commit is None or not isinstance(commit, Commit):
            return None

    d: Dict[str, BlobEntry] = {}
    for blob_id, blob_name, unit_id, metric in analyze_unit(commit.tree):
        d.setdefault(blob_id, {"name": blob_name, "metrics": [], "units": {}})[
            "units"
        ].setdefault(unit_id, []).append(metric)
    for blob_id, blob_name, metric in analyze_blob(commit.tree):
        d.setdefault(blob_id, {"name": blob_name, "metrics": [], "units": {}})[
            "metrics"
        ].append(metric)
    output = parse_commit(
        commit,
        metrics=analyze_tree(commit.tree),
        blobs=[
            BlobOutput(
                id=str(blob_id),
                name=blob["name"],
                metrics=blob["metrics"],
                units=[
                    UnitOutput(id=unit_id, metrics=unit)
                    for unit_id, unit in blob["units"].items()
                ],
            )
            for blob_id, blob in d.items()
        ],
    )
    return dumps(output, separators=(",", ":"), indent=None)
