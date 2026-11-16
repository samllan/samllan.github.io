"""Make deterministic folds from known group IDs in a synthetic example.

The archive includes CLAM split tooling. This original illustration uses a
greedy split to demonstrate core grouping, as in the grading chapter. That
chapter did not establish slide- or participant-grouped validation.
"""
import csv
import sys
from collections import defaultdict


def assign_folds(records, fold_count):
    by_group = defaultdict(list)
    samples = set()
    for sample, group in records:
        if sample in samples:
            raise ValueError(f"Duplicate sample: {sample}")
        samples.add(sample)
        by_group[group].append(sample)
    if not 2 <= fold_count <= len(by_group):
        raise ValueError("Provide at least two folds and one group per fold")

    sizes = [0] * fold_count
    assignments = {}
    for group, members in sorted(by_group.items(), key=lambda item: (-len(item[1]), item[0])):
        fold = min(range(fold_count), key=lambda index: sizes[index])
        sizes[fold] += len(members)
        assignments.update(dict.fromkeys(members, fold))
    return assignments


if __name__ == "__main__":
    records = [("a", "g1"), ("b", "g1"), ("c", "g2"), ("d", "g3")]
    writer = csv.writer(sys.stdout)
    writer.writerow(("sample", "held_out_fold"))
    writer.writerows(sorted(assign_folds(records, fold_count=2).items()))
