from cProfile import Profile
from pstats import Stats

from pyrepositoryminer.analyze import analyze

"""
Set the globals in analyze.py as follows:

repo: Repository = Repository(".../numpy.git")

tm: Tuple[str, ...] = tuple([])
bm: Tuple[str, ...] = tuple(["linecount"])
um: Tuple[str, ...] = tuple([])
"""


def main() -> None:
    with open("commits copy.txt", "r") as f:
        commits = tuple(line.strip() for line in f)
    profile = Profile()
    profile.enable()
    for commit in commits[:50]:
        analyze(commit)
    profile.disable()
    profile_stats = Stats(profile).sort_stats("cumtime")
    profile_stats.print_stats()


if __name__ == "__main__":
    main()
