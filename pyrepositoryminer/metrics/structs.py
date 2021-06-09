from typing import Any, NamedTuple, Optional

from pyrepositoryminer.visitableobject import VisitableBlob


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
