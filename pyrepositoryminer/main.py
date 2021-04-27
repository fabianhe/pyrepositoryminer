from pathlib import Path
from tempfile import TemporaryDirectory

from pygit2 import (
    GIT_SORT_REVERSE,
    GIT_SORT_TOPOLOGICAL,
    Blob,
    Repository,
    Tree,
    Walker,
    clone_repository,
)
from typer import Typer, echo

app = Typer()


def get_filecount(tree: Tree) -> int:
    n_files: int = 0
    for obj in tree:
        if isinstance(obj, Blob):
            n_files += 1
        elif isinstance(obj, Tree):
            n_files += get_filecount(obj)
    return n_files


def get_loc(tree: Tree) -> int:
    n_loc: int = 0
    for obj in tree:
        if isinstance(obj, Blob):
            if not obj.is_binary:
                n_loc += len(obj.data.split(b"\n"))
        elif isinstance(obj, Tree):
            n_loc += get_loc(obj)
    return n_loc


@app.command()
def clone(
    url: str,
    path: Path,
    bare: bool = True,
) -> None:
    "Clone a repository to a path."
    clone_repository(url, path, bare=bare)
    echo(f"Cloned {url} to {path}")


@app.command()
def local_filecount(path: Path, simplify_first_parent: bool = True) -> None:
    """Get the number of files per commit in each branch in a local repository."""
    repo = Repository(path)
    for branch_name in repo.branches:
        branch = repo.branches[branch_name]
        walker: Walker = repo.walk(
            branch.peel().id, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
        )
        if simplify_first_parent:
            walker.simplify_first_parent()
        for commit in walker:
            echo(
                "{:s},{:d},{:s},{:d}".format(
                    branch_name,
                    commit.commit_time,
                    str(commit.id),
                    get_filecount(commit.tree),
                )
            )


@app.command()
def filecount(
    url: str, checkout_branch: str, simplify_first_parent: bool = True
) -> None:
    """Get the number of files per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo: Repository = clone_repository(
            url, tmpdirname, checkout_branch=checkout_branch, bare=True
        )
        walker = repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE)
        if simplify_first_parent:
            walker.simplify_first_parent()
        for commit in walker:
            echo(f"{commit.id},{get_filecount(commit.tree)}")


@app.command()
def loc(url: str, checkout_branch: str, simplify_first_parent: bool = True) -> None:
    """Get the lines of code per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo: Repository = clone_repository(
            url, tmpdirname, checkout_branch=checkout_branch, bare=True
        )
        walker = repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE)
        if simplify_first_parent:
            walker.simplify_first_parent()
        for commit in walker:
            echo(f"{commit.id},{get_loc(commit.tree)}")
