from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Optional

from typer import Argument, Option
from typer.models import FileText

from pyrepositoryminer.commands.utils.metric import AvailableMetrics

if TYPE_CHECKING:
    from multiprocessing.pool import Pool as tcpool


@contextmanager
def make_pool(
    workers: int,
    repository: Path,
    metrics: List[AvailableMetrics],
    custom_metrics: List[str],
) -> Iterator["tcpool"]:
    from multiprocessing import Pool  # pylint: disable=import-outside-toplevel

    from pyrepositoryminer.analyze import (  # pylint: disable=import-outside-toplevel
        InitArgs,
        initialize,
    )
    from pyrepositoryminer.commands.utils.metric import (  # pylint: disable=import-outside-toplevel
        import_metric,
    )
    from pyrepositoryminer.metrics import (  # pylint: disable=import-outside-toplevel
        all_metrics,
    )

    with Pool(
        max(workers, 1),
        initialize,
        (
            InitArgs(
                repository,
                tuple({metric.value for metric in metrics} & all_metrics.keys()),
                tuple(map(import_metric, set(custom_metrics))),
            ),
        ),
    ) as pool:
        yield pool


def analyze(
    repository: Path = Argument(..., help="The path to the bare repository."),
    metrics: Optional[List[AvailableMetrics]] = Argument(None, case_sensitive=False),
    commits: Optional[FileText] = Option(
        None,
        help="The newline-separated input file of commit ids. Commit ids are read from stdin if this is not passed.",  # pylint: disable=line-too-long
    ),
    custom_metrics: List[str] = Option([]),
    workers: int = 1,
) -> None:
    """Analyze commits of a repository.

    Either provide the commit ids to analyze on stdin or as a file argument."""
    from sys import stdin  # pylint: disable=import-outside-toplevel

    from pyrepositoryminer.analyze import (  # pylint: disable=import-outside-toplevel
        worker,
    )

    metrics = metrics if metrics else []
    ids = (
        id.strip()
        for id in (commits if commits else stdin)  # pylint: disable=superfluous-parens
    )
    with make_pool(workers, repository, metrics, custom_metrics) as pool:
        results = (res for res in pool.imap(worker, ids) if res is not None)
        for result in results:
            print(result)
