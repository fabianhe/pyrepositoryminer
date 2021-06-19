"""Analyze a commit w.r.t tree-, blob- or unit-metrics.

Global variables are accessed in the context of a worker.
"""
from asyncio import run
from asyncio.tasks import as_completed
from pathlib import Path
from typing import Awaitable, Callable, Iterable, NamedTuple, Optional, Tuple

from pygit2 import Commit, Repository
from uvloop import install

from pyrepositoryminer.metrics import NativeBlobMetrics  # type: ignore
from pyrepositoryminer.metrics.nativeblob.main import NativeBlobVisitor
from pyrepositoryminer.metrics.structs import BlobTuple, Metric
from pyrepositoryminer.output import CommitOutput, format_output, parse_commit
from pyrepositoryminer.visitableobject import VisitableObject


class InitArgs(NamedTuple):
    repository: Path
    native_blob_metrics: Tuple[str, ...]


repo: Repository
native_blob_metrics: Tuple[Callable[[BlobTuple], Awaitable[Iterable[Metric]]], ...]
native_blob_visitor: NativeBlobVisitor


async def categorize_metrics(
    *futures: Awaitable[Iterable[Metric]],
) -> Tuple[Iterable[Metric], Iterable[Metric], Iterable[Metric]]:
    toplevel = []
    objectlevel = []
    subobjectlevel = []
    for future in as_completed(futures):
        for metric in await future:
            if metric.object is None:
                toplevel.append(metric)
            elif metric.subobject is None:
                objectlevel.append(metric)
            else:
                subobjectlevel.append(metric)
    return toplevel, objectlevel, subobjectlevel


async def analyze(commit_id: str) -> Optional[CommitOutput]:
    global repo, native_blob_metrics
    try:
        commit = repo.get(commit_id)
    except ValueError:
        return None
    else:
        if commit is None or not isinstance(commit, Commit):
            return None
    root = VisitableObject.from_object(commit.tree)
    futures = [
        m(blob_tup)
        async for blob_tup in native_blob_visitor(root)
        for m in native_blob_metrics
    ]
    return parse_commit(commit, *(await categorize_metrics(*futures)))


def initialize(init_args: InitArgs) -> None:
    global repo, native_blob_metrics, native_blob_visitor
    repo = Repository(init_args.repository)
    native_blob_metrics = tuple(
        NativeBlobMetrics[m]() for m in init_args.native_blob_metrics
    )
    native_blob_visitor = NativeBlobVisitor()
    install()


def worker(commit_id: str) -> Optional[str]:
    output = run(analyze(commit_id))
    if output is None:
        return None
    return format_output(output)
