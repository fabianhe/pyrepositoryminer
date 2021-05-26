from subprocess import PIPE, Popen

from pyrepositoryminer.metrics.blob import BlobMetric
from pyrepositoryminer.visitableobject import VisitableBlob


class Linecount(BlobMetric):
    def is_filtered(self, blob: VisitableBlob) -> bool:
        return bool(blob.obj.is_binary)

    def analyze_blob_value(self, blob: VisitableBlob) -> int:
        output, _ = Popen(
            ["wc", "-l"], stdin=PIPE, stdout=PIPE, stderr=PIPE
        ).communicate(blob.obj.data)
        return int(output)
