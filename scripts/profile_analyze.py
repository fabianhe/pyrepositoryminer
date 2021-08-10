from cProfile import Profile
from pathlib import Path
from pstats import Stats

from typer import FileText

from pyrepositoryminer.commands.analyze import analyze
from pyrepositoryminer.commands.utils.metric import AvailableMetrics


def main() -> None:
    p = Path("/Users/fabian/bare-repos/numpy.git")
    with open("commits copy.txt", "rb") as f:
        c = FileText(f)
        analyze(p, [AvailableMetrics["filecount"]], c)


if __name__ == "__main__":
    profile = Profile()
    profile.enable()
    main()
    profile.disable()
    profile_stats = Stats(profile).sort_stats("tottime")
    profile_stats.print_stats()
