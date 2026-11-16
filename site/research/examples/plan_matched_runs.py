"""Make a run schedule that varies one setting against a shared baseline."""
from itertools import product


def plan_runs(baseline, changes, folds, seeds):
    configurations = {"baseline": baseline}
    for name, (key, value) in changes.items():
        if name in configurations or key not in baseline or baseline[key] == value:
            raise ValueError(f"Invalid single change: {name}")
        configurations[name] = {**baseline, key: value}
    for name, fold, seed in product(configurations, folds, seeds):
        yield {"configuration": name, "fold": fold, "seed": seed, **configurations[name]}


if __name__ == "__main__":
    base = {"pool": "mean", "batch_size": 16}
    changes = {"max_pool": ("pool", "max"), "large_batch": ("batch_size", 32)}
    for run in plan_runs(base, changes, folds=(0, 1), seeds=(7, 11)):
        print(run)
