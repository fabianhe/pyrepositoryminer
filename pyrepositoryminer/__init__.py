from tempfile import TemporaryDirectory

from pygit2 import GIT_SORT_REVERSE, GIT_SORT_TOPOLOGICAL, Blob, Tree, clone_repository
from typer import Typer, echo

app = Typer()


def count(tree) -> int:
    n_files: int = 0
    for obj in tree:
        if isinstance(obj, Blob):
            n_files += 1
        elif isinstance(obj, Tree):
            n_files += count(obj)
    return n_files


@app.command()
def main(url: str, checkout_branch: str):
    with TemporaryDirectory() as tmpdirname:
        repo = clone_repository(url, tmpdirname, checkout_branch=checkout_branch)
        for commit in repo.walk(
            repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
        ):
            echo(f"{commit.id},{count(commit.tree)}")


if __name__ == "__main__":
    app()
