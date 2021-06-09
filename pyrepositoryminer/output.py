from json import dumps
from typing import Any, Dict, Iterable, List, TypedDict

from pygit2 import Commit, Signature

from pyrepositoryminer.metrics.structs import Metric as AnalysisMetric


class Metric(TypedDict):
    name: str
    cached: bool
    value: Any


class ObjectOutput(TypedDict):
    id: str
    metrics: List[Metric]


class SuperObjectOutput(ObjectOutput):
    name: str
    subobjects: List[ObjectOutput]


class SignatureOutput(TypedDict):
    email: str
    name: str
    time_offset: int
    time: int


class CommitOutput(ObjectOutput):
    author: SignatureOutput
    commit_time: int
    commit_time_offset: int
    committer: SignatureOutput
    message: str
    parent_ids: List[str]
    objects: List[SuperObjectOutput]


def parse_signature(signature: Signature) -> SignatureOutput:
    return SignatureOutput(
        email=str(signature.email),
        name=str(signature.name),
        time_offset=int(signature.offset),
        time=int(signature.time),
    )


def parse_commit(
    commit: Commit,
    toplevel: Iterable[AnalysisMetric],
    objectlevel: Iterable[AnalysisMetric],
    subobjectlevel: Iterable[AnalysisMetric],
) -> CommitOutput:
    d: Dict[str, SuperObjectOutput] = {}
    for metric in subobjectlevel:
        m = Metric(name=metric.name, cached=metric.cached, value=metric.value)
        subobjects = d.setdefault(
            metric.object.oid,  # type: ignore
            SuperObjectOutput(
                id=metric.object.oid,  # type: ignore
                name=metric.object.name,  # type: ignore
                metrics=[],
                subobjects=[],
            ),
        )["subobjects"]
        v = [
            subobject for subobject in subobjects if subobject["id"] == metric.subobject
        ]
        if v:
            v[0]["metrics"].append(m)
        else:
            o = ObjectOutput(id=metric.subobject, metrics=[m])  # type: ignore
            subobjects.append(o)
    for metric in objectlevel:
        d.setdefault(
            metric.object.oid,  # type: ignore
            SuperObjectOutput(
                id=metric.object.oid,  # type: ignore
                name=metric.object.name,  # type: ignore
                metrics=[],
                subobjects=[],
            ),
        )["metrics"].append(
            Metric(name=metric.name, cached=metric.cached, value=metric.value)
        )
    return CommitOutput(
        id=str(commit.id),
        author=parse_signature(commit.author),
        commit_time=int(commit.commit_time),
        commit_time_offset=int(commit.commit_time_offset),
        committer=parse_signature(commit.committer),
        message=str(commit.message),
        parent_ids=[str(id) for id in commit.parent_ids],
        metrics=list(
            Metric(name=m.name, cached=m.cached, value=m.value) for m in toplevel
        ),
        objects=list(d.values()),
    )


def format_output(output: CommitOutput) -> str:
    return dumps(output, separators=(",", ":"), indent=None)
