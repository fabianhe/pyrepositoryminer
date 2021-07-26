from json import dumps
from typing import Dict

from pydriller import Repository

repo = Repository("/Users/fabian/bare-repos/numpy.git", only_in_branch="main")
commits = repo.traverse_commits()
files: Dict[str, int] = {}
for commit in commits:
    for file in commit.modified_files:
        renamed = file.old_path is not None
        deleted = file.new_path is None
        if renamed or deleted:
            files.pop(file.old_path)
    updates = (file for file in commit.modified_files if file.new_path is not None)
    files.update({file.new_path: file.nloc for file in updates})
    print(
        dumps({"id": commit.hash, "files": files}, separators=(",", ":"), indent=None)
    )
