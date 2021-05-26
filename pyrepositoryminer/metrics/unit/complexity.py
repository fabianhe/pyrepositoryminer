from typing import Iterable, Tuple

from radon.complexity import cc_visit

from pyrepositoryminer.metrics.unit import UnitMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Complexity(UnitMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return not str(blob.obj.name).endswith(".py")

    def analyze_unit_values(self, blob: VisitableBlob) -> Iterable[Tuple[str, int]]:
        complexities = cc_visit(blob.obj.data)
        for u in complexities:
            yield str(u.fullname), int(u.complexity)
