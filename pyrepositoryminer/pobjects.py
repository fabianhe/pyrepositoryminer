from __future__ import annotations

from typing import Any, Iterator, Sequence

from pygit2 import Blob as pBlob
from pygit2 import Commit as pCommit
from pygit2 import Object as pObject
from pygit2 import Tree as pTree


class Object:
    @classmethod
    def from_pobject(cls, obj: pObject) -> Object:
        if isinstance(obj, pBlob):
            return Blob(obj)
        if isinstance(obj, pTree):
            return Tree(obj)
        if isinstance(obj, pCommit):
            return Commit(obj)
        return Object(obj)

    def __init__(self, obj: pObject) -> None:
        self.obj = obj

    @property
    def id(self) -> str:
        return str(self.obj.id)

    @property
    def name(self) -> str:
        if (s := self.obj.name) is None:
            return ""
        return str(s)


class Commit(Object):
    @property
    def parents(self) -> Sequence[Commit]:
        return tuple(Commit(parent) for parent in self.obj.parents)

    @property
    def tree(self) -> Tree:
        return Tree(self.obj.tree)


class Tree(Object):
    def __iter__(self) -> Iterator[Object]:
        return (Object.from_pobject(obj) for obj in self.obj)

    def __getitem__(self, item: Any) -> Object:
        return Object.from_pobject(self.obj[item])


class Blob(Object):
    @property
    def is_binary(self) -> bool:
        return bool(self.obj.is_binary)

    @property
    def data(self) -> bytes:
        return bytes(self.obj.data)

    @property
    def size(self) -> int:
        return int(self.obj.size)
