from json import dumps
from typing import Any, Iterable, List, TypedDict

from pygit2 import Commit, Signature


class Metric(TypedDict):
    name: str
    value: Any


class ObjectOutput(TypedDict):
    id: str


class UnitOutput(ObjectOutput):
    metrics: List[Metric]


class BlobOutput(ObjectOutput):
    metrics: List[Metric]
    units: List[UnitOutput]


class SignatureOutput(TypedDict):
    email: str
    name: str
    time_offset: int
    time: int


class CommitBase(ObjectOutput):
    author: SignatureOutput
    commit_time: int
    commit_time_offset: int
    committer: SignatureOutput
    message: str
    parent_ids: List[str]


class CommitOutput(CommitBase, total=False):
    metrics: List[Metric]
    blobs: List[BlobOutput]


def parse_signature(signature: Signature) -> SignatureOutput:
    return SignatureOutput(
        email=str(signature.email),
        name=str(signature.name),
        time_offset=int(signature.offset),
        time=int(signature.time),
    )


def parse_commit(
    commit: Commit,
    metrics: Iterable[Metric],
    blobs: Iterable[BlobOutput],
) -> CommitOutput:
    return CommitOutput(
        id=str(commit.id),
        author=parse_signature(commit.author),
        commit_time=int(commit.commit_time),
        commit_time_offset=int(commit.commit_time_offset),
        committer=parse_signature(commit.committer),
        message=str(commit.message),
        parent_ids=[str(id) for id in commit.parent_ids],
        metrics=list(metrics),
        blobs=list(blobs),
    )


def format_output(output: CommitOutput) -> str:
    return dumps(output, separators=(",", ":"), indent=None)
