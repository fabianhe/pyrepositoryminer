from pathlib import Path

from pygit2 import clone_repository


def clone(url: str, path: Path, bare: bool = True) -> None:
    "Clone a repository to a path."
    clone_repository(url, path, bare=bare)
