from pathlib import Path
from typing import Iterable

from typer import Argument


def branch(
    repository: Path = Argument(..., help="The path to the bare repository."),
    local: bool = True,
    remote: bool = False,
) -> None:
    """Get the branches of a repository."""
    from pygit2 import Repository  # pylint: disable=import-outside-toplevel
    from typer import echo  # pylint: disable=import-outside-toplevel

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
