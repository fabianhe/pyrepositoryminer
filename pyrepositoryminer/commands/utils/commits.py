from itertools import filterfalse
from typing import Hashable, Iterable, Set, TypeVar

from pygit2 import Repository, Walker

T = TypeVar("T", bound=Hashable)


def iter_distinct(iterable: Iterable[T]) -> Iterable[T]:
    seen: Set[T] = set()
    for element in filterfalse(seen.__contains__, iterable):
        seen.add(element)
        yield element


def generate_walkers(
    repo: Repository,
    branch_names: Iterable[str],
    simplify_first_parent: bool,
    sorting: int,
) -> Iterable[Walker]:
    walkers = tuple(
        repo.walk(repo.branches[branch_name].peel().id, sorting)
        for branch_name in branch_names
    )
    for walker in walkers if simplify_first_parent else tuple():
        walker.simplify_first_parent()
    yield from walkers
