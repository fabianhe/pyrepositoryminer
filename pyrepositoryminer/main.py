from collections import defaultdict
from enum import Enum
from itertools import chain
from pathlib import Path
from sys import stdin
from typing import DefaultDict, Iterable, List, Optional, Set, Tuple, TypedDict

from pygit2 import (
    GIT_SORT_NONE,
    GIT_SORT_REVERSE,
    GIT_SORT_TIME,
    GIT_SORT_TOPOLOGICAL,
    Commit,
    Repository,
    Walker,
    clone_repository,
)
from typer import Argument, FileText, Option, Typer, echo

from pyrepositoryminer.metrics import BlobMetrics, TreeMetrics, UnitMetrics

from .helper import BlobOutput, Metric, UnitOutput, format_output, parse_commit
from .visitableobject import VisitableTree

app = Typer(help="Efficient Repository Mining in Python.")

AvailableMetrics = Enum(  # type: ignore
    "AvailableMetrics",
    sorted((key, key) for key in {*TreeMetrics, *BlobMetrics, *UnitMetrics}),
)


class Sort(str, Enum):
    topological = "topological"
    time = "time"


class blobhelper(TypedDict):
    metrics: List[Metric]
    units: DefaultDict[str, List[Metric]]


blobshelper = DefaultDict[str, blobhelper]


def validate_metrics(
    metrics: Optional[List[AvailableMetrics]],
) -> Tuple[Set[str], Set[str], Set[str]]:
    if metrics is None:
        return (set(), set(), set())
    distinct = {metric.value for metric in metrics}
    return (
        distinct & TreeMetrics.keys(),
        distinct & BlobMetrics.keys(),
        distinct & UnitMetrics.keys(),
    )


def validate_commits(
    repository: Repository, commit_ids: Iterable[str]
) -> Iterable[Commit]:
    for commit_id in commit_ids:
        try:
            obj = repository.get(commit_id)
        except ValueError:
            continue
        else:
            if obj is None or not isinstance(obj, Commit):
                continue
        yield obj


def walk_commits(
    repo: Repository, branch_name: str, simplify_first_parent: bool
) -> Iterable[Commit]:
    branch = repo.branches[branch_name]
    walker: Walker = repo.walk(
        branch.peel().id, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
    )
    if simplify_first_parent:
        walker.simplify_first_parent()
    yield from walker


@app.command()
def commits(
    repository: Path,
    branches: Optional[FileText] = None,
    simplify_first_parent: bool = True,
    drop_duplicates: bool = False,
    sort: Optional[Sort] = Option(None, case_sensitive=False),
    sort_reverse: bool = False,
) -> None:
    """Get the commit ids of a repository."""
    repo = Repository(repository)
    sorting = GIT_SORT_NONE
    if sort == "topological":
        sorting = GIT_SORT_TOPOLOGICAL
    elif sort == "time":
        sorting = GIT_SORT_TIME
    if sort_reverse:
        sorting |= GIT_SORT_REVERSE
    walkers = []
    for branch_name in (
        branch_name.strip() for branch_name in (stdin if branches is None else branches)
    ):
        branch = repo.branches[branch_name]
        walker: Walker = repo.walk(branch.peel().id)
        if simplify_first_parent:
            walker.simplify_first_parent()
        walkers.append(walker)
    all_commits: Iterable[Commit] = chain(*walkers)
    if drop_duplicates:
        all_commits = set(all_commits)
    for commit in all_commits:
        echo(str(commit.id))


@app.command()
def analyze(
    repository: Path,
    metrics: Optional[List[AvailableMetrics]] = Argument(None, case_sensitive=False),
    commits: Optional[FileText] = None,
) -> None:
    """Analyze commits of a repository."""
    tree_m, blob_m, unit_m = validate_metrics(metrics)
    for commit in validate_commits(
        Repository(repository),
        (commit_id.strip() for commit_id in (stdin if commits is None else commits)),
    ):
        blobs: blobshelper = defaultdict(
            lambda: {"metrics": [], "units": defaultdict(list)}
        )
        for m in unit_m:
            for res in UnitMetrics[m]().visitTree(VisitableTree(commit.tree)).result:
                blobs[res.blob_id]["units"][res.unit_id].append(
                    Metric(name=m, value=res.value)
                )
        for m in blob_m:
            for res in BlobMetrics[m]().visitTree(VisitableTree(commit.tree)).result:
                blobs[res.blob_id]["metrics"].append(Metric(name=m, value=res.value))
        d = parse_commit(
            commit,
            metrics=[
                Metric(
                    name=m,
                    value=TreeMetrics[m]()
                    .visitTree(VisitableTree(commit.tree))
                    .result.value,
                )
                for m in tree_m
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
        echo(format_output(d))


@app.command()
def clone(
    url: str,
    path: Path,
) -> None:
    "Clone a repository to a path."
    clone_repository(url, path, bare=True)


@app.command()
def branch(path: Path, local: bool = True, remote: bool = True) -> None:
    """Get the branches of a repository."""
    repo = Repository(path)
    branches: Iterable[str] = tuple()
    if local and remote:
        branches = repo.branches
    elif local:
        branches = repo.branches.local
    elif remote:
        branches = repo.branches.remote
    for branch_name in branches:
        echo(branch_name)
