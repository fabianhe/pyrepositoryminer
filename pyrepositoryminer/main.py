from collections import defaultdict
from pathlib import Path
from sys import stdin
from typing import (
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypedDict,
)

from pygit2 import (
    GIT_SORT_REVERSE,
    GIT_SORT_TOPOLOGICAL,
    Commit,
    Repository,
    Walker,
    clone_repository,
)
from typer import Argument, FileText, Typer, echo

from .helper import BlobOutput, Metric, UnitOutput, format_output, parse_commit
from .treevisitor import (
    BlobMetric,
    ComplexityVisitor,
    FilecountVisitor,
    LineLengthVisitor,
    LocVisitor,
    NestingVisitor,
    RawVisitor,
    TreeMetric,
    UnitMetric,
)
from .visitableobject import VisitableTree

app = Typer()


class blobhelper(TypedDict):
    metrics: List[Metric]
    units: DefaultDict[str, List[Metric]]


blobshelper = DefaultDict[str, blobhelper]


TREE_METRICS: Dict[str, Type[TreeMetric]] = {
    "filecount": FilecountVisitor,
    "loc": LocVisitor,
}

BLOB_METRICS: Dict[str, Type[BlobMetric]] = {
    "nesting": NestingVisitor,
    "raw": RawVisitor,
}

UNIT_METRICS: Dict[str, Type[UnitMetric]] = {
    "complexity": ComplexityVisitor,
    "linelength": LineLengthVisitor,
}


def validate_metrics(
    metrics: Optional[Iterable[str]],
) -> Tuple[Set[str], Set[str], Set[str]]:
    if metrics is None:
        return (set(), set(), set())
    distinct = set(metrics)
    return (
        distinct.intersection(TREE_METRICS.keys()),
        distinct.intersection(BLOB_METRICS.keys()),
        distinct.intersection(UNIT_METRICS.keys()),
    )


def validate_commits(
    repository: Repository, commit_ids: Iterable[str]
) -> Iterable[Commit]:
    for commit_id in commit_ids:
        try:
            obj = repository.get(commit_id)
        except ValueError:
            pass
        if obj is not None and isinstance(obj, Commit):
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
def analyze(
    repository: Path,
    metrics: Optional[List[str]] = Argument(None),
    commits: Optional[FileText] = None,
) -> None:
    tree_m, blob_m, unit_m = validate_metrics(metrics)
    for commit in validate_commits(
        Repository(repository),
        (commit_id.strip() for commit_id in (stdin if commits is None else commits)),
    ):
        blobs: blobshelper = defaultdict(
            lambda: {"metrics": [], "units": defaultdict(list)}
        )
        for m in unit_m:
            for res in UNIT_METRICS[m]().visitTree(VisitableTree(commit.tree)).result:
                blobs[res.blob_id]["units"][res.unit_id].append(
                    Metric(name=m, value=res.value)
                )
        for m in blob_m:
            for res in BLOB_METRICS[m]().visitTree(VisitableTree(commit.tree)).result:
                blobs[res.blob_id]["metrics"].append(Metric(name=m, value=res.value))
        d = parse_commit(
            commit,
            metrics=[
                Metric(
                    name=m,
                    value=TREE_METRICS[m]()
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
    echo(f"Cloned {url} to {path}")


@app.command()
def branch(path: Path, local: bool = True, remote: bool = True) -> None:
    repo = Repository(path)
    branches: Iterable[str] = tuple()
    if local and remote:
        branches = repo.branches
    elif local and not remote:
        branches = repo.branches.local
    elif not local and remote:
        branches = repo.branches.remote
    for branch_name in branches:
        echo(branch_name)


@app.command()
def complexity(path: Path, simplify_first_parent: bool = True) -> None:
    """Get the maximum complexity per file per commit per branch.

    Currently, only Python files are supported."""
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            for blob_id, result in (
                ComplexityVisitor().visitTree(VisitableTree(commit.tree)).result
            ):
                echo(
                    "{:s},{:s},{:s},{:d}".format(
                        branch_name, str(commit.id), str(blob_id), result
                    )
                )


@app.command()
def raw(path: Path, simplify_first_parent: bool = True) -> None:
    """Get raw metrics per file per commit per branch.

    Currently, only Python files are supported.
    Raw metrics are:
    1. LOC:
       The number of lines of code (total)
    2. LLOC:
       The number of logical lines of code
    3. SLOC:
       The number of source lines of code (not necessarily corresponding to the LLOC)
    """
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            for blob_id, result in (
                RawVisitor().visitTree(VisitableTree(commit.tree)).result
            ):
                echo(
                    "{:s},{:s},{:s},{:d},{:d},{:d}".format(
                        branch_name,
                        str(commit.id),
                        str(blob_id),
                        result.loc,
                        result.lloc,
                        result.sloc,
                    )
                )


@app.command()
def nesting(path: Path, simplify_first_parent: bool = True) -> None:
    """Get nesting level per file per commit per branch."""
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            for blob_id, result in (
                NestingVisitor().visitTree(VisitableTree(commit.tree)).result
            ):
                echo(
                    "{:s},{:s},{:s},{:d}".format(
                        branch_name,
                        str(commit.id),
                        str(blob_id),
                        result,
                    )
                )


@app.command()
def filecount(path: Path, simplify_first_parent: bool = True) -> None:
    """Get the number of files per commit in each branch in a local repository."""
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            echo(
                "{:s},{:s},{:d}".format(
                    branch_name,
                    str(commit.id),
                    FilecountVisitor().visitTree(VisitableTree(commit.tree)).result,
                )
            )
