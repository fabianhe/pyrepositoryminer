from dataclasses import dataclass
from typing import Any, NamedTuple, Optional

from pyrepositoryminer.visitableobject import (
    VisitableBlob,
    VisitableCommit,
    VisitableTree,
)


@dataclass(frozen=True)
class BaseMetricInput:
    is_cached: bool


@dataclass(frozen=True)
class DirMetricInput(BaseMetricInput):
    path: str
    tree: VisitableTree


@dataclass(frozen=True)
class NativeTreeMetricInput(BaseMetricInput):
    tree: VisitableTree
    commit: VisitableCommit


@dataclass(frozen=True)
class NativeBlobMetricInput(BaseMetricInput):
    path: str
    blob: VisitableBlob


class ObjectIdentifier(NamedTuple):
    oid: str
    name: str


class Metric(NamedTuple):
    name: str
    value: Any
    cached: bool
    object: Optional[ObjectIdentifier] = None
    subobject: Optional[str] = None
