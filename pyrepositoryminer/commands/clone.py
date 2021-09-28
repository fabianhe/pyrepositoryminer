from pathlib import Path


def clone(url: str, path: Path, bare: bool = True) -> None:
    "Clone a repository to a path."
    from pygit2 import clone_repository  # pylint: disable=import-outside-toplevel

    clone_repository(url, path, bare=bare)
