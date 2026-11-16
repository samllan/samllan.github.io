"""Report uneven cell counts across the cores represented in a cell index."""
from collections import Counter
from statistics import median


def describe_counts(core_ids, indexed_cells):
    counts = dict.fromkeys(core_ids, 0)
    for core, count in Counter(indexed_cells).items():
        if core not in counts:
            raise ValueError(f"Unknown core: {core}")
        counts[core] = count
    if not counts:
        raise ValueError("Supply at least one core")
    total = sum(counts.values())
    return {
        "counts": counts, "cells": total, "median_cells_per_core": median(counts.values()),
        "largest_core_share": max(counts.values()) / total if total else 0,
    }


if __name__ == "__main__":
    print(describe_counts(["A", "B", "C"], ["A", "A", "A", "B"]))
