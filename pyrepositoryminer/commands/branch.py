from pathlib import Path
from typing import Iterable

from pygit2 import Repository
from typer import Argument, echo


def branch(
    repository: Path = Argument(..., help="The path to the bare repository."),
    local: bool = True,
    remote: bool = False,
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
