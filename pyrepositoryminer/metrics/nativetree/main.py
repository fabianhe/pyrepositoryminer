from abc import ABC
from typing import Optional

from pyrepositoryminer.metrics.main import BaseMetric, BaseVisitor
from pyrepositoryminer.metrics.structs import NativeTreeMetricInput
from pyrepositoryminer.pobjects import Commit, Object


class NativeTreeVisitor(BaseVisitor):
    def __call__(self, visitable_object: Object) -> Optional[NativeTreeMetricInput]:
        if not isinstance(visitable_object, Commit):
            return None
        output = NativeTreeMetricInput(
            self.oid_is_cached(visitable_object.tree.id),
            visitable_object.tree,
            visitable_object,
        )
        self.cache_oid(visitable_object.tree.id)
        return output


class NativeTreeMetric(BaseMetric[NativeTreeMetricInput], ABC):
    pass
