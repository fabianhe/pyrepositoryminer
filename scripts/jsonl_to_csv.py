from json import loads
from typing import Any, Dict, Iterable, List, Tuple

from pyrepositoryminer.analyze import CommitOutput


def jsonl_to_csv(file: str) -> Iterable[str]:
    results: Dict[str, List[Tuple[Any, ...]]] = {
        "COMMITS": [],
        "PARENTS": [],
        "METRICS": [],
        "BLOBS": [],
        "BLOB_METRICS": [],
        "UNITS": [],
        "UNIT_METRICS": [],
    }
    with open("out.jsonl") as f:
        for line in f:
            d: CommitOutput = loads(line)
            results["COMMITS"].append(
                (
                    d["id"],
                    d["author"]["email"],
                    d["author"]["name"],
                    d["author"]["time"],
                    d["author"]["time_offset"],
                    d["commit_time"],
                    d["committer"]["email"],
                    d["committer"]["name"],
                    d["committer"]["time"],
                    d["committer"]["time_offset"],
                    d["message"],
                )
            )
            for parent_id in d["parent_ids"]:
                results["PARENTS"].append((d["id"], parent_id))
            for metric in d["metrics"]:
                results["METRICS"].append(
                    (
                        d["id"],
                        metric["name"],
                        metric.get("value", None),
                        metric.get("cached", False),
                    )
                )
            for blob in d["blobs"]:
                results["BLOBS"].append((d["id"], blob["id"], blob["name"]))
                for metric in blob["metrics"]:
                    results["BLOB_METRICS"].append(
                        (
                            blob["id"],
                            metric["name"],
                            metric.get("value", None),
                            metric.get("cached", False),
                        )
                    )
                for unit in blob["units"]:
                    results["UNITS"].append((blob["id"], unit["id"]))
                    for metric in unit["metrics"]:
                        results["UNIT_METRICS"].append(
                            (
                                blob["id"],
                                unit["id"],
                                metric["name"],
                                metric.get("value", None),
                                metric.get("cached", False),
                            )
                        )

    for table_name, table in results.items():
        yield (table_name)
        for row in table:
            yield (",".join(str(cell) for cell in row))
