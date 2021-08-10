from itertools import islice
from json import dumps
from sys import argv
from typing import Dict

from pydriller import Repository

repo = Repository(
    argv[1],
    order="topo-order",
    only_in_branch="main" if "numpy" in argv[1] else "master",
)
commits = islice(repo.traverse_commits(), 100)
files: Dict[str, int] = {}
for commit in commits:
    for file in commit.modified_files:
        renamed = file.old_path is not None
        deleted = file.new_path is None
        if renamed or deleted:
            files.pop(file.old_path, None)
    updates = (file for file in commit.modified_files if file.new_path is not None)
    files.update({file.new_path: file.nloc for file in updates})
    print(
        dumps({"id": commit.hash, "files": files}, separators=(",", ":"), indent=None)
    )
