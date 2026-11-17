"""Compare a fixed validation window across paired training runs."""
from collections import defaultdict
from math import isfinite
from statistics import mean


def summarise_traces(records, *, baseline, variants, run_pairs, start_epoch, stop_epoch):
    configs = (baseline, *variants)
    expected = {(name, fold, seed) for name in configs for fold, seed in run_pairs}
    epochs = set(range(start_epoch, stop_epoch + 1))
    if not expected or not epochs or len(configs) != len(set(configs)):
        raise ValueError("Provide distinct configurations, paired runs and an epoch window")
    traces = defaultdict(dict)
    for name, fold, seed, epoch, score, elapsed in records:
        key = (name, fold, seed)
        if key not in expected:
            raise ValueError(f"Unexpected run: {key}")
        if epoch in traces[key]:
            raise ValueError(f"Duplicate epoch for {key}: {epoch}")
        if not isfinite(score) or not 0 <= score <= 1 or not isfinite(elapsed) or elapsed < 0:
            raise ValueError(f"Invalid score or elapsed time for {key}")
        traces[key][epoch] = score, elapsed

    result = {}
    for name in configs:
        summaries = []
        for key in sorted(run for run in expected if run[0] == name):
            if not epochs <= traces[key].keys():
                raise ValueError(f"Incomplete validation window for {key}")
            scores, times = zip(*(traces[key][epoch] for epoch in sorted(epochs)))
            if any(earlier > later for earlier, later in zip(times, times[1:])):
                raise ValueError(f"Elapsed time decreases for {key}")
            summaries.append((mean(scores), times[-1]))
        scores, times = zip(*summaries)
        result[name] = mean(scores), mean(times)
    return result


if __name__ == "__main__":
    pairs = [(0, 11), (1, 11)]
    records = [
        (name, fold, seed, epoch, base + 0.01 * (fold + epoch), seconds * epoch)
        for name, base, seconds in (("baseline", 0.73, 22), ("variant", 0.74, 17))
        for fold, seed in pairs for epoch in (1, 2, 3)
    ]
    for name, (score, time) in summarise_traces(
        records, baseline="baseline", variants=["variant"], run_pairs=pairs, start_epoch=2, stop_epoch=3
    ).items():
        print(f"{name}: mean balanced accuracy {score:.3f}, mean time {time:.1f}s")
