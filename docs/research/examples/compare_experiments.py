"""Compare experiment variants against matched baseline runs.

Pair runs on the same validation fold and seed. Report the mean percentage
change in error, time per epoch and peak memory. The measurements below
are illustrative and use two folds and one seed.
"""

from itertools import product
from math import isfinite
from statistics import mean
from typing import NamedTuple


class Measurements(NamedTuple):
    error: float
    seconds_per_epoch: float
    peak_memory_mib: float


class Run(NamedTuple):
    configuration: str
    fold: int
    seed: int
    metrics: Measurements


def compare_experiments(runs, *, baseline, variants, folds, seeds):
    """Require one result for each configured run before comparing variants."""
    pairs = list(product(folds, seeds))
    if not pairs or len(pairs) != len(set(pairs)):
        raise ValueError("Specify a nonempty design with distinct folds and seeds.")
    configurations = (baseline, *variants)
    if len(configurations) != len(set(configurations)):
        raise ValueError("Baseline and variants must have distinct names.")

    results = {}
    for run in runs:
        key = (run.configuration, run.fold, run.seed)
        if key in results or any(not isfinite(value) or value < 0 for value in run.metrics):
            raise ValueError(f"Duplicate run or invalid measurement: {key}")
        results[key] = run.metrics

    expected = {(name, fold, seed) for name in configurations for fold, seed in pairs}
    if results.keys() != expected:
        missing = len(expected - results.keys())
        unexpected = len(results.keys() - expected)
        raise ValueError(f"Run design mismatch: {missing} missing, {unexpected} unexpected.")

    baseline_runs = [results[baseline, fold, seed] for fold, seed in pairs]
    if any(value == 0 for run in baseline_runs for value in run):
        raise ValueError("Percentage changes require nonzero baseline measurements.")

    # Form each ratio within its matched pair before averaging across runs.
    comparisons = {}
    for name in configurations[1:]:
        variant_runs = [results[name, fold, seed] for fold, seed in pairs]
        changes = [
            tuple(100 * (value / base - 1) for value, base in zip(variant, reference))
            for variant, reference in zip(variant_runs, baseline_runs)
        ]
        comparisons[name] = Measurements(*(mean(metric) for metric in zip(*changes)))
    return comparisons


if __name__ == "__main__":
    runs = [
        Run("baseline", 0, 7, Measurements(0.31, 52, 92)),
        Run("compact", 0, 7, Measurements(0.32, 29, 60)),
        Run("baseline", 1, 7, Measurements(0.33, 55, 91)),
        Run("compact", 1, 7, Measurements(0.34, 31, 59)),
    ]
    for name, change in compare_experiments(
        runs, baseline="baseline", variants=("compact",), folds=(0, 1), seeds=(7,)
    ).items():
        print(f"{name} | error {change.error:+.1f}% | time {change.seconds_per_epoch:+.1f}% "
              f"| memory {change.peak_memory_mib:+.1f}%")
