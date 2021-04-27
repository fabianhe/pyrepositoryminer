from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from pygit2 import (
    GIT_SORT_REVERSE,
    GIT_SORT_TOPOLOGICAL,
    Repository,
    Walker,
    clone_repository,
)
from typer import Typer, echo

from .treevisitor import FilecountVisitor, LocVisitor
from .visitableobject import VisitableTree

app = Typer()


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
            visitor = FilecountVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(
                "{:s},{:d},{:s},{:d}".format(
                    branch_name,
                    commit.commit_time,
                    str(commit.id),
                    visitor.result,
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
            visitor = FilecountVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(f"{commit.id},{visitor.result}")


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
            visitor = LocVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(f"{commit.id},{visitor.result}")
