from typing import Any, NamedTuple, Optional

from pyrepositoryminer.visitableobject import VisitableBlob, VisitableTree


class DirTuple(NamedTuple):
    path: str
    is_cached: bool


class TreeTuple(NamedTuple):
    tree: VisitableTree
    is_cached: bool


class BlobTuple(NamedTuple):
    path: str
    blob: VisitableBlob
    is_cached: bool


class ObjectIdentifier(NamedTuple):
    oid: str
    name: str


class Metric(NamedTuple):
    name: str
    value: Any
    cached: bool
    object: Optional[ObjectIdentifier] = None
    subobject: Optional[str] = None
