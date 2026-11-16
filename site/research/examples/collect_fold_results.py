"""Read several CSV files with a shared run-metrics schema."""
import argparse
import csv
from io import StringIO


def collect_results(streams):
    rows = {}
    required = {"configuration", "fold", "seed", "metric"}
    for stream in streams:
        reader = csv.DictReader(stream)
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("CSV requires configuration, fold, seed and metric columns")
        for row in reader:
            key = (row["configuration"], int(row["fold"]), int(row["seed"]))
            if key in rows:
                raise ValueError(f"Duplicate result: {key}")
            rows[key] = float(row["metric"])
    return dict(sorted(rows.items()))


if __name__ == "__main__":
    from contextlib import ExitStack
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="*")
    args = parser.parse_args()
    with ExitStack() as stack:
        streams = [stack.enter_context(path.open(encoding="utf-8", newline="")) for path in args.files]
        if not streams:
            streams = [StringIO("configuration,fold,seed,metric\nbaseline,0,11,0.28\n")]
        for key, metric in collect_results(streams).items():
            print(*key, metric, sep=",")
