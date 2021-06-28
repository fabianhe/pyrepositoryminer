from typing import Any, Dict

import pyrepositoryminer.metrics.dir as DirMetrics
import pyrepositoryminer.metrics.nativeblob as NativeBlobMetrics
import pyrepositoryminer.metrics.nativetree as NativeTreeMetrics

all_metrics: Dict[str, Any] = {
    **{
        getattr(NativeBlobMetrics, m).name: getattr(NativeBlobMetrics, m)
        for m in NativeBlobMetrics.__all__
    },
    **{
        getattr(NativeTreeMetrics, m).name: getattr(NativeTreeMetrics, m)
        for m in NativeTreeMetrics.__all__
    },
    **{getattr(DirMetrics, m).name: getattr(DirMetrics, m) for m in DirMetrics.__all__},
}
__all__ = ("all_metrics", "NativeBlobMetrics", "NativeTreeMetrics", "DirMetrics")
