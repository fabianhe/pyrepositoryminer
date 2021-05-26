from typing import Iterable, Tuple

from pyrepositoryminer.metrics.unit import UnitMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Linelength(UnitMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return bool(blob.obj.is_binary)

    def analyze_unit_values(self, blob: VisitableBlob) -> Iterable[Tuple[str, int]]:
        for i, line in enumerate(blob.obj.data.split(b"\n")):
            yield f"L{i+1}", len(line)
