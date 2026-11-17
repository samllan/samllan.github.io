"""Read saved grading predictions and build a table of comparable errors."""
import argparse
import csv
from collections import defaultdict
from io import StringIO
from pathlib import Path
from math import isfinite
from statistics import mean


def build_table(predictions):
    errors = defaultdict(dict)
    references = {}
    for row in csv.DictReader(predictions):
        scale, sample = row["scale"], row["sample"]
        if sample in errors[scale]:
            raise ValueError(f"Repeated held-out prediction: {scale}/{sample}")
        reference, prediction = float(row["reference"]), float(row["prediction"])
        if not isfinite(reference) or not isfinite(prediction):
            raise ValueError(f"Invalid grade for {scale}/{sample}")
        assignment = row["fold"], reference
        if references.setdefault(sample, assignment) != assignment:
            raise ValueError(f"Inconsistent fold or reference grade for {sample}")
        errors[scale][sample] = abs(prediction - reference)
    first = next(iter(errors.values()), {})
    if not first or any(samples.keys() != first.keys() for samples in errors.values()):
        raise ValueError("The table requires the same nonempty sample set for all scales")
    return [(scale, len(samples), mean(samples.values())) for scale, samples in sorted(errors.items())]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, nargs="?")
    args = parser.parse_args()
    sample = "sample,scale,fold,reference,prediction\na,patch,0,2,2.2\na,core,0,2,1.6\n"
    stream = args.predictions.open(encoding="utf-8", newline="") if args.predictions else StringIO(sample)
    with stream:
        print("scale,samples,mae")
        for scale, count, error in build_table(stream):
            print(f"{scale},{count},{error:.3f}")
