"""Compare an experiment with a baseline on matching validation folds and seeds."""

import argparse
import csv
from itertools import product
from math import isfinite
from pathlib import Path
from statistics import mean


METRICS = ('error', 'seconds', 'peak_memory_mb')


def read_runs(csv_path):
    runs = {}
    with csv_path.open(newline='', encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            key = row['experiment'], int(row['fold']), int(row['seed'])
            values = tuple(float(row[metric]) for metric in METRICS)
            if key in runs or any(not isfinite(value) or value < 0 for value in values):
                raise ValueError(f'Duplicate run or invalid measurement: {key}')
            runs[key] = values
    return runs


def compare(runs, baseline, folds, seeds):
    experiments = sorted({name for name, _, _ in runs})
    if baseline not in experiments:
        raise ValueError(f'Baseline {baseline!r} is missing.')
    pairs = list(product(folds, seeds))
    expected = set(product(experiments, folds, seeds))
    if set(runs) != expected:
        raise ValueError(f'Run design mismatch: {len(expected - runs.keys())} missing, '
                         f'{len(runs.keys() - expected)} unexpected.')
    for name in experiments:
        differences = [tuple(value - reference for value, reference in zip(
            runs[name, fold, seed], runs[baseline, fold, seed])) for fold, seed in pairs]
        yield name, *(mean(metric) for metric in zip(*differences))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('--baseline', default='baseline')
    parser.add_argument('--folds', type=int, nargs='+', default=[0, 1])
    parser.add_argument('--seeds', type=int, nargs='+', default=[7, 12])
    args = parser.parse_args()
    print('Experiment  Change in error, seconds, and peak memory (MB)')
    for name, *deltas in compare(read_runs(args.results), args.baseline, sorted(set(args.folds)), sorted(set(args.seeds))):
        print(f'{name:<10}  {deltas[0]:+7.3f}  {deltas[1]:+9.2f}  {deltas[2]:+18.1f}')
