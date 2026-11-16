"""Turn individual ratings into a reference while preserving disagreement."""
from collections import defaultdict
from math import isfinite
from statistics import mean


def reference_grades(ratings):
    ratings_by_sample = defaultdict(dict)
    for sample, assessor, score in ratings:
        if not isfinite(score) or assessor in ratings_by_sample[sample]:
            raise ValueError(f"Duplicate or invalid rating for {sample}/{assessor}")
        ratings_by_sample[sample][assessor] = score
    return {
        sample: (mean(scores.values()), len(scores), max(scores.values()) - min(scores.values()))
        for sample, scores in sorted(ratings_by_sample.items())
    }


if __name__ == "__main__":
    for sample, summary in reference_grades([("a", "r1", 1), ("a", "r2", 2), ("b", "r2", 3)]).items():
        print(sample, *summary, sep=",")
