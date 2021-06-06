from enum import Enum
from itertools import filterfalse, islice
from json import loads
from multiprocessing import Pool
from pathlib import Path
from sys import stdin
from typing import Any, Dict, Hashable, Iterable, List, Optional, Set, Tuple, TypeVar

from pygit2 import (
    GIT_SORT_NONE,
    GIT_SORT_REVERSE,
    GIT_SORT_TIME,
    GIT_SORT_TOPOLOGICAL,
    Repository,
    Walker,
    clone_repository,
)
from typer import Argument, FileText, Option, Typer, echo

from pyrepositoryminer.analyze import CommitOutput
from pyrepositoryminer.analyze import analyze as analyze_worker
from pyrepositoryminer.analyze import initialize as initialize_worker
from pyrepositoryminer.metrics import BlobMetrics, TreeMetrics, UnitMetrics

app = Typer(help="Efficient Repository Mining in Python.")

AvailableMetrics = Enum(  # type: ignore
    "AvailableMetrics",
    sorted((key, key) for key in {*TreeMetrics, *BlobMetrics, *UnitMetrics}),
)


class Sort(str, Enum):
    topological = "topological"
    time = "time"


SORTINGS: Dict[Optional[str], int] = {
    "topological": GIT_SORT_TOPOLOGICAL,
    "time": GIT_SORT_TIME,
    None: GIT_SORT_NONE,
}


T = TypeVar("T", bound=Hashable)


def iter_distinct(iterable: Iterable[T]) -> Iterable[T]:
    seen: Set[T] = set()
    for element in filterfalse(seen.__contains__, iterable):
        seen.add(element)
        yield element


def validate_metrics(
    metrics: Optional[List[AvailableMetrics]],
) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    distinct: Set[str] = (
        set() if metrics is None else {metric.value for metric in metrics}
    )
    return (
        tuple(sorted(distinct & TreeMetrics.keys())),
        tuple(sorted(distinct & BlobMetrics.keys())),
        tuple(sorted(distinct & UnitMetrics.keys())),
    )


def generate_walkers(
    repo: Repository,
    branch_names: Iterable[str],
    simplify_first_parent: bool,
    sorting: int,
) -> Iterable[Walker]:
    walkers = tuple(
        repo.walk(repo.branches[branch_name.strip()].peel().id, sorting)
        for branch_name in branch_names
    )
    for walker in walkers if simplify_first_parent else tuple():
        walker.simplify_first_parent()
    yield from walkers


@app.command()
def commits(
    repository: Path = Argument(..., help="The path to the repository."),
    branches: Optional[FileText] = Option(
        None, help="The branches to pull the commits from."
    ),
    simplify_first_parent: bool = True,
    drop_duplicates: bool = False,
    sort: Optional[Sort] = Option(None, case_sensitive=False),
    sort_reverse: bool = False,
    limit: Optional[int] = None,
) -> None:
    """Get the commit ids of a repository."""
    commit_ids: Iterable[str] = (
        str(commit.id)
        for walker in generate_walkers(
            Repository(repository),
            stdin if branches is None else branches,
            simplify_first_parent,
            SORTINGS[sort] if not sort_reverse else (SORTINGS[sort] | GIT_SORT_REVERSE),
        )
        for commit in walker
    )
    commit_ids = commit_ids if not drop_duplicates else iter_distinct(commit_ids)
    commit_ids = commit_ids if limit is None else islice(commit_ids, limit)
    for commit_id in commit_ids:
        echo(commit_id)


@app.command()
def analyze(
    repository: Path,
    metrics: Optional[List[AvailableMetrics]] = Argument(None, case_sensitive=False),
    commits: Optional[FileText] = None,
    workers: int = 1,
) -> None:
    """Analyze commits of a repository."""
    ids = (id.strip() for id in (stdin if commits is None else commits))
    with Pool(
        max(workers, 1), initialize_worker, (repository, *validate_metrics(metrics))
    ) as pool:
        results = (res for res in pool.imap(analyze_worker, ids) if res is not None)
        for result in results:
            echo(result)


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
    branches: Iterable[str]
    if local and remote:
        branches = repo.branches
    elif local:
        branches = repo.branches.local
    elif remote:
        branches = repo.branches.remote
    for branch_name in branches:
        echo(branch_name)


@app.command()
def to_csv() -> None:
    """Format a JSONL input as CSV."""

    results: Dict[str, List[Tuple[Any, ...]]] = {
        "COMMITS": [],
        "PARENTS": [],
        "METRICS": [],
        "BLOBS": [],
        "BLOB_METRICS": [],
        "UNITS": [],
        "UNIT_METRICS": [],
    }
    for line in stdin:
        d: CommitOutput = loads(line)
        results["COMMITS"].append(
            (
                d["id"],
                d["author"]["email"],
                d["author"]["name"],
                d["author"]["time"],
                d["author"]["time_offset"],
                d["commit_time"],
                d["committer"]["email"],
                d["committer"]["name"],
                d["committer"]["time"],
                d["committer"]["time_offset"],
                d["message"],
            )
        )
        for parent_id in d["parent_ids"]:
            results["PARENTS"].append((d["id"], parent_id))
        for metric in d["metrics"]:
            results["METRICS"].append(
                (
                    d["id"],
                    metric["name"],
                    metric.get("value", None),
                    metric.get("cached", False),
                )
            )
        for blob in d["blobs"]:
            results["BLOBS"].append((d["id"], blob["id"], blob["name"]))
            for metric in blob["metrics"]:
                results["BLOB_METRICS"].append(
                    (
                        blob["id"],
                        metric["name"],
                        metric.get("value", None),
                        metric.get("cached", False),
                    )
                )
            for unit in blob["units"]:
                results["UNITS"].append((blob["id"], unit["id"]))
                for metric in unit["metrics"]:
                    results["UNIT_METRICS"].append(
                        (
                            blob["id"],
                            unit["id"],
                            metric["name"],
                            metric.get("value", None),
                            metric.get("cached", False),
                        )
                    )
    for table_name, table in results.items():
        echo(table_name)
        for row in table:
            echo(",".join(str(cell) for cell in row))
