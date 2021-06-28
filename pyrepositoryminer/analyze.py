"""Analyze a commit w.r.t tree-, blob- or unit-metrics.

Global variables are accessed in the context of a worker.
"""
from asyncio import run
from asyncio.tasks import as_completed
from pathlib import Path
from typing import Any, Awaitable, Iterable, NamedTuple, Optional, Tuple

from pygit2 import Commit, Repository
from uvloop import install

from pyrepositoryminer.metrics import all_metrics
from pyrepositoryminer.metrics.dir.main import DirMetric, DirVisitor
from pyrepositoryminer.metrics.nativeblob.main import (
    NativeBlobMetric,
    NativeBlobVisitor,
)
from pyrepositoryminer.metrics.nativetree.main import (
    NativeTreeMetric,
    NativeTreeVisitor,
)
from pyrepositoryminer.metrics.structs import Metric
from pyrepositoryminer.output import CommitOutput, format_output, parse_commit
from pyrepositoryminer.visitableobject import VisitableObject


class InitArgs(NamedTuple):
    repository: Path
    metrics: Tuple[str, ...]


repo: Repository
native_blob_metrics: Tuple[Any, ...]
native_blob_visitor: NativeBlobVisitor
native_tree_metrics: Tuple[Any, ...]
native_tree_visitor: NativeTreeVisitor
dir_metrics: Tuple[Any, ...]
dir_visitor: DirVisitor


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
    root = VisitableObject.from_object(commit)
    futures = [
        m(blob_tup)
        async for blob_tup in native_blob_visitor(root)
        for m in native_blob_metrics
        if not (await m.filter(blob_tup))
    ]
    tree_tup = await native_tree_visitor(root)
    futures.extend(m(tree_tup) for m in native_tree_metrics)
    await dir_visitor(root)
    async with dir_visitor:
        futures.extend(m(dir_visitor.dir_tup) for m in dir_metrics)
        mets = await categorize_metrics(*futures)
    return parse_commit(commit, *mets)


def initialize(init_args: InitArgs) -> None:
    install()
    global repo
    global native_blob_metrics, native_blob_visitor
    global native_tree_metrics, native_tree_visitor
    global dir_metrics, dir_visitor
    repo = Repository(init_args.repository)
    native_blob_metrics = tuple(
        all_metrics[m]()
        for m in init_args.metrics
        if issubclass(all_metrics[m], NativeBlobMetric)
    )
    native_blob_visitor = NativeBlobVisitor()
    native_tree_metrics = tuple(
        all_metrics[m]()
        for m in init_args.metrics
        if issubclass(all_metrics[m], NativeTreeMetric)
    )
    native_tree_visitor = NativeTreeVisitor()
    dir_metrics = tuple(
        all_metrics[m]()
        for m in init_args.metrics
        if issubclass(all_metrics[m], DirMetric)
    )
    dir_visitor = DirVisitor(repo)


def worker(commit_id: str) -> Optional[str]:
    output = run(analyze(commit_id))
    if output is None:
        return None
    return format_output(output)
