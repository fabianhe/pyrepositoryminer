from dataclasses import dataclass
from typing import Any, NamedTuple, Optional

from pyrepositoryminer.pobjects import Blob, Commit, Tree


@dataclass(frozen=True)
class BaseMetricInput:
    is_cached: bool


@dataclass(frozen=True)
class DirMetricInput(BaseMetricInput):
    path: str
    tree: Tree


@dataclass(frozen=True)
class NativeTreeMetricInput(BaseMetricInput):
    tree: Tree
    commit: Commit


@dataclass(frozen=True)
class NativeBlobMetricInput(BaseMetricInput):
    path: str
    blob: Blob


class ObjectIdentifier(NamedTuple):
    oid: str
    name: str


class Metric(NamedTuple):
    name: str
    value: Any
    cached: bool
    object: Optional[ObjectIdentifier] = None
    subobject: Optional[str] = None
