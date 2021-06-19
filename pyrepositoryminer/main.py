from enum import Enum
from itertools import filterfalse, islice
from multiprocessing import Pool
from pathlib import Path
from sys import stdin
from typing import Dict, Hashable, Iterable, List, Optional, Set, Tuple, TypeVar

from pygit2 import (
    GIT_SORT_NONE,
    GIT_SORT_REVERSE,
    GIT_SORT_TIME,
    GIT_SORT_TOPOLOGICAL,
    Repository,
    Walker,
    clone_repository,
)
from typer import Argument, Option, Typer, echo

from pyrepositoryminer.analyze import InitArgs, initialize, worker
from pyrepositoryminer.metrics import NativeBlobMetrics  # type: ignore

app = Typer(help="Efficient Repository Mining in Python.")

AvailableMetrics = Enum(  # type: ignore
    "AvailableMetrics",
    sorted((key, key) for key in {*NativeBlobMetrics}),
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
) -> Tuple[Tuple[str, ...]]:
    distinct: Set[str] = (
        set() if metrics is None else {metric.value for metric in metrics}
    )
    return (tuple(sorted(distinct & NativeBlobMetrics.keys())),)


def generate_walkers(
    repo: Repository,
    branch_names: Iterable[str],
    simplify_first_parent: bool,
    sorting: int,
) -> Iterable[Walker]:
    walkers = tuple(
        repo.walk(repo.branches[branch_name].peel().id, sorting)
        for branch_name in branch_names
    )
    for walker in walkers if simplify_first_parent else tuple():
        walker.simplify_first_parent()
    yield from walkers


@app.command()
def commits(
    repository: Path = Argument(..., help="The path to the bare repository."),
    branches: Path = Argument(
        "-",
        allow_dash=True,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        help="The newline-separated input file of branches to pull the commits from. Branches are read from stdin if this is not passed.",  # noqa: E501
    ),
    simplify_first_parent: bool = True,
    drop_duplicates: bool = False,
    sort: Optional[Sort] = Option(None, case_sensitive=False),
    sort_reverse: bool = False,
    limit: Optional[int] = None,
) -> None:
    """Get the commit ids of a repository.

    Either provide the branches to get the commit ids from on stdin or as a file argument."""  # noqa: E501
    branch_names: Iterable[str]
    if branches != Path("-"):
        with open(branches) as f:
            branch_names = [line for line in f]
    else:
        branch_names = (line for line in stdin)
    branch_names = (branch.strip() for branch in branch_names)
    commit_ids: Iterable[str] = (
        str(commit.id)
        for walker in generate_walkers(
            Repository(repository),
            branch_names,
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
    repository: Path = Argument(..., help="The path to the bare repository."),
    commits: Path = Argument(
        "-",
        allow_dash=True,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        help="The newline-separated input file of commit ids. Commit ids are read from stdin if this is not passed.",  # noqa: E501
    ),
    metrics: Optional[List[AvailableMetrics]] = Argument(None, case_sensitive=False),
    workers: int = 1,
) -> None:
    """Analyze commits of a repository.

    Either provide the commit ids to analyze on stdin or as a file argument."""
    ids: Iterable[str]
    if commits != Path("-"):
        with open(commits) as f:
            ids = [line for line in f]
    else:
        ids = (line for line in stdin)
    ids = (id.strip() for id in ids)
    native_blob_metrics = (
        tuple()
        if metrics is None
        else tuple(sorted({m.value for m in metrics if m.value in NativeBlobMetrics}))
    )
    with Pool(
        max(workers, 1),
        initialize,
        (InitArgs(repository, native_blob_metrics),),
    ) as pool:
        results = (res for res in pool.imap(worker, ids) if res is not None)
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
def branch(
    repository: Path = Argument(..., help="The path to the bare repository."),
    local: bool = True,
    remote: bool = True,
) -> None:
    """Get the branches of a repository."""
    repo = Repository(repository)
    branches: Iterable[str]
    if local and remote:
        branches = repo.branches
    elif local:
        branches = repo.branches.local
    elif remote:
        branches = repo.branches.remote
    for branch_name in branches:
        echo(branch_name)
