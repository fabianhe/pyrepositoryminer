from typing import Any, Dict

from radon.metrics import h_visit

from pyrepositoryminer.metrics.blob import BlobMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Halstead(BlobMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return not str(blob.obj.name).endswith(".py")

    def analyze_blob_value(self, blob: VisitableBlob) -> Dict[str, Any]:
        return dict(h_visit(blob.obj.data.decode()).total._asdict())
