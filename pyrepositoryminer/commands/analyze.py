from enum import Enum
from functools import reduce
from importlib import import_module
from inspect import isclass
from multiprocessing import Pool
from pathlib import Path
from sys import stdin
from typing import List, Optional

from typer import Abort, Argument, Option, echo
from typer.models import FileText

from pyrepositoryminer.analyze import InitArgs, initialize, worker
from pyrepositoryminer.metrics import all_metrics
from pyrepositoryminer.metrics.dir.main import DirMetric
from pyrepositoryminer.metrics.nativeblob.main import NativeBlobMetric
from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric

AvailableMetrics = Enum(  # type: ignore
    # https://github.com/python/mypy/issues/5317
    "AvailableMetrics",
    [(k, k) for k in sorted(all_metrics.keys())],
)


def import_metric(import_str: str):  # type: ignore  # TODO make this a metric abc
    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        echo(f'Import string "{import_str}" must be in format "<module>:<attribute>"')
        raise Abort()
    try:
        module = import_module(module_str)
    except ImportError as e:
        if e.name != module_str:
            raise e from None
        echo(f'Could not import module "{module_str}"')
        raise Abort()
    try:
        instance = reduce(getattr, (module, *attrs_str.split(".")))  # type: ignore
    except AttributeError:
        print(f'Attribute "{attrs_str}" not found in module "{module_str}"')
        raise Abort()
    if not isclass(instance):
        print(f'Instance "{instance}" must be a class')
        raise Abort()
    parents = (NativeBlobMetric, NativeTreeMetric, DirMetric)
    if not any(issubclass(instance, parent) for parent in parents):  # type: ignore
        print(f'Instance "{instance}" must subclass a pyrepositoryminer metric class')
        raise Abort()
    return instance


def analyze(
    repository: Path = Argument(..., help="The path to the bare repository."),
    metrics: Optional[List[AvailableMetrics]] = Argument(None, case_sensitive=False),
    commits: Optional[FileText] = Option(
        None,
        help="The newline-separated input file of commit ids. Commit ids are read from stdin if this is not passed.",  # noqa: E501
    ),
    custom_metrics: List[str] = Option([]),
    workers: int = 1,
) -> None:
    """Analyze commits of a repository.

    Either provide the commit ids to analyze on stdin or as a file argument."""
    metrics = metrics if metrics else []
    ids = (id.strip() for id in (commits if commits else stdin))
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
        results = (res for res in pool.imap(worker, ids) if res is not None)
        for result in results:
            echo(result)
