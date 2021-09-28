from enum import Enum
from functools import reduce
from inspect import isclass

from typer import Abort, echo

from pyrepositoryminer.metrics import all_metrics
from pyrepositoryminer.metrics.diffblob.main import DiffBlobMetric
from pyrepositoryminer.metrics.diffdir.main import DiffDirMetric
from pyrepositoryminer.metrics.dir.main import DirMetric
from pyrepositoryminer.metrics.nativeblob.main import NativeBlobMetric
from pyrepositoryminer.metrics.nativetree.main import NativeTreeMetric

AvailableMetrics = Enum(  # type: ignore
    # https://github.com/python/mypy/issues/5317
    "AvailableMetrics",
    [(k, k) for k in sorted(all_metrics.keys())],
)


def import_metric(import_str: str):  # type: ignore  # TODO make this a metric abc
    from importlib import import_module  # pylint: disable=import-outside-toplevel

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
        raise Abort() from e
    try:
        instance = reduce(getattr, (module, *attrs_str.split(".")))  # type: ignore
    except AttributeError as e:
        print(f'Attribute "{attrs_str}" not found in module "{module_str}"')
        raise Abort() from e
    if not isclass(instance):
        print(f'Instance "{instance}" must be a class')
        raise Abort()
    parents = (
        NativeBlobMetric,
        DiffBlobMetric,
        NativeTreeMetric,
        DirMetric,
        DiffDirMetric,
    )
    if not any(issubclass(instance, parent) for parent in parents):  # type: ignore
        print(f'Instance "{instance}" must subclass a pyrepositoryminer metric class')
        raise Abort()
    return instance
