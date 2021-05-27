from typing import Any, Dict, Iterable, Tuple

from radon.metrics import h_visit

from pyrepositoryminer.metrics.unit import UnitMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Halstead(UnitMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return not str(blob.obj.name).endswith(".py")

    def analyze_unit_values(
        self, blob: VisitableBlob
    ) -> Iterable[Tuple[str, Dict[str, Any]]]:
        try:
            for function_name, report in h_visit(blob.obj.data).functions:
                yield function_name, report._asdict()
        except SyntaxError:
            pass  # TODO append an error output?
