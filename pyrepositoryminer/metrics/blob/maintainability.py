from radon.metrics import mi_visit

from pyrepositoryminer.metrics.blob import BlobMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Maintainability(BlobMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return not str(blob.obj.name).endswith(".py")

    def analyze_blob_value(self, blob: VisitableBlob) -> float:
        return float(mi_visit(blob.obj.data.decode(), multi=True))
