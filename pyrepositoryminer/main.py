from tempfile import TemporaryDirectory

from pygit2 import GIT_SORT_REVERSE, GIT_SORT_TOPOLOGICAL, Blob, Tree, clone_repository
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
def filecount(url: str, checkout_branch: str) -> None:
    """Get the number of files per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo = clone_repository(url, tmpdirname, checkout_branch=checkout_branch)
        for commit in repo.walk(
            repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
        ):
            echo(f"{commit.id},{get_filecount(commit.tree)}")


@app.command()
def loc(url: str, checkout_branch: str) -> None:
    """Get the lines of code per commit."""
    with TemporaryDirectory() as tmpdirname:
        repo = clone_repository(url, tmpdirname, checkout_branch=checkout_branch)
        for commit in repo.walk(
            repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
        ):
            echo(f"{commit.id},{get_loc(commit.tree)}")
