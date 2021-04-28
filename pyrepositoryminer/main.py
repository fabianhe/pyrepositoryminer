from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from pygit2 import (
    GIT_SORT_REVERSE,
    GIT_SORT_TOPOLOGICAL,
    Commit,
    Repository,
    Walker,
    clone_repository,
)
from typer import Typer, echo

from .treevisitor import ComplexityVisitor, FilecountVisitor, LocVisitor, RawVisitor
from .visitableobject import VisitableTree

app = Typer()


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
def complexity(path: Path, simplify_first_parent: bool = True) -> None:
    """Get the maximum complexity per file per commit per branch.

    Currently, only Python files are supported."""
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            visitor = ComplexityVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            for blob_id, max_complexity in visitor.result:
                echo(f"{branch_name},{str(commit.id)},{blob_id},{max_complexity}")


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
            visitor = RawVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            for result in visitor.result:
                echo(
                    "{:s},{:s},{:d},{:d},{:d}".format(
                        branch_name,
                        str(commit.id),
                        result.loc,
                        result.lloc,
                        result.sloc,
                    )
                )


@app.command()
def filecount(path: Path, simplify_first_parent: bool = True) -> None:
    """Get the number of files per commit in each branch in a local repository."""
    repo = Repository(path)
    for branch_name in repo.branches:
        for commit in walk_commits(repo, branch_name, simplify_first_parent):
            visitor = FilecountVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(
                "{:s},{:s},{:d}".format(
                    branch_name,
                    str(commit.id),
                    visitor.result,
                )
            )


@app.command()
def remote_filecount(
    url: str, checkout_branch: str, simplify_first_parent: bool = True
) -> None:
    """Get the number of files per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo: Repository = clone_repository(
            url, tmpdirname, checkout_branch=checkout_branch, bare=True
        )
        for commit in walk_commits(repo, repo.head.shorthand, simplify_first_parent):
            visitor = FilecountVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(f"{repo.head.shorthand},{commit.id},{visitor.result}")


@app.command()
def remote_loc(
    url: str, checkout_branch: str, simplify_first_parent: bool = True
) -> None:
    """Get the lines of code per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo: Repository = clone_repository(
            url, tmpdirname, checkout_branch=checkout_branch, bare=True
        )
        for commit in walk_commits(repo, repo.head.shorthand, simplify_first_parent):
            visitor = LocVisitor()
            visitor.visitTree(VisitableTree(commit.tree))
            echo(f"{repo.head.shorthand},{commit.id},{visitor.result}")
