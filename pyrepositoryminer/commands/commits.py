from enum import Enum
from itertools import islice
from pathlib import Path
from sys import stdin
from typing import Hashable, Iterable, Optional, TypeVar

from pygit2 import (
    GIT_SORT_NONE,
    GIT_SORT_REVERSE,
    GIT_SORT_TIME,
    GIT_SORT_TOPOLOGICAL,
    Repository,
)
from typer import Argument, Option


class Sort(str, Enum):
    topological = "topological"
    time = "time"
    none = "none"

    def __init__(self, name: str) -> None:
        self.sort_name = name
        super().__init__()

    @property
    def flag(self):  # type: ignore
        return {
            "topological": GIT_SORT_TOPOLOGICAL,
            "time": GIT_SORT_TIME,
            "none": GIT_SORT_NONE,
        }[self.sort_name]


T = TypeVar("T", bound=Hashable)


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
        help="The newline-separated input file of branches to pull the commits from. Branches are read from stdin if this is not passed.",  # pylint: disable=line-too-long
    ),
    simplify_first_parent: bool = True,
    drop_duplicates: bool = True,
    sort: Sort = Option(Sort.topological, case_sensitive=False),
    sort_reverse: bool = True,
    limit: Optional[int] = None,
) -> None:
    """Get the commit ids of a repository.

    Either provide the branches to get the commit ids from on stdin or as a file argument."""  # pylint: disable=line-too-long
    from typer import echo  # pylint: disable=import-outside-toplevel

    from pyrepositoryminer.commands.utils.commits import (  # pylint: disable=import-outside-toplevel
        generate_walkers,
        iter_distinct,
    )

    branch_names: Iterable[str]
    if branches != Path("-"):
        with open(branches, encoding="utf-8") as f:
            branch_names = list(f)
    else:
        branch_names = (line for line in stdin)
    branch_names = (branch.strip() for branch in branch_names)
    commit_ids: Iterable[str] = (
        str(commit.id)
        for walker in generate_walkers(
            Repository(repository),
            branch_names,
            simplify_first_parent,
            sort.flag if not sort_reverse else (sort.flag | GIT_SORT_REVERSE),
        )
        for commit in walker
    )
    commit_ids = commit_ids if not drop_duplicates else iter_distinct(commit_ids)
    commit_ids = commit_ids if limit is None else islice(commit_ids, limit)
    for commit_id in commit_ids:
        echo(commit_id)
