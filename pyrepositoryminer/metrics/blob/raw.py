from typing import Any, Dict

from radon.raw import analyze

from pyrepositoryminer.metrics.blob import BlobMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Raw(BlobMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return not str(blob.obj.name).endswith(".py")

    def analyze_blob_value(self, blob: VisitableBlob) -> Dict[str, Any]:
        return dict(analyze(blob.obj.data.decode())._asdict())
