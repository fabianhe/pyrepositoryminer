from enum import Enum
from itertools import chain
from json import dumps
from multiprocessing import Manager, Pool
from pathlib import Path
from sys import stdin
from typing import Dict, Iterable, List, Optional, Set, Tuple

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
    repository: Path = Argument(..., help="The path to the repository."),
    branches: Optional[FileText] = Option(
        None, help="The branches to pull the commits from."
    ),
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
    workers: int = 1,
) -> None:
    """Analyze commits of a repository."""
    workers = max(workers, 1)
    tree_m, blob_m, unit_m = validate_metrics(metrics)

    manager = Manager()
    cache: Dict[str, bool] = manager.dict()
    with Pool(
        max(workers, 1), initialize_worker, (repository, tree_m, blob_m, unit_m, cache)
    ) as pool:
        for result in pool.imap(
            analyze_worker,
            (
                commit_id.strip()
                for commit_id in (stdin if commits is None else commits)
            ),
        ):
            if result is not None:
                echo(dumps(result, separators=(",", ":"), indent=None))


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
