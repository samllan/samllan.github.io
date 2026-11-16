"""Check whether every expected model run has comparable resource measurements."""
from math import isfinite


def audit_measurements(expected_runs, measurements):
    issues = []
    for run in expected_runs:
        logs = measurements.get(run)
        if logs is None:
            issues.append((run, "run missing"))
            continue
        for metric in ("seconds_per_epoch", "peak_memory_mib"):
            value = logs.get(metric)
            if value is None or not isfinite(value) or value <= 0:
                issues.append((run, f"missing or invalid {metric}"))
    return issues


if __name__ == "__main__":
    expected = [("baseline", 0), ("compact", 0)]
    measured = {("baseline", 0): {"seconds_per_epoch": 10.4}}
    print(audit_measurements(expected, measured))
