"""Turn a matched run plan into a scheduler-independent job manifest."""
import argparse
from hashlib import sha256
import json

from plan_matched_runs import plan_runs


def job_manifest(schedule):
    jobs = {}
    for specification in schedule:
        text = json.dumps(specification, sort_keys=True, separators=(",", ":"), allow_nan=False)
        identifier = sha256(text.encode("utf-8")).hexdigest()[:16]
        if identifier in jobs:
            raise ValueError(f"Repeated job specification: {identifier}")
        jobs[identifier] = {"run_id": identifier, "specification": specification}
    return list(jobs.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    schedule = plan_runs(
        {"pool": "mean", "batch_size": 16}, {"max_pool": ("pool", "max")},
        folds=(0, 1), seeds=(7, 11),
    )
    print(json.dumps(job_manifest(schedule), indent=2))
