"""Summarise waiting times from the fictional reading room pilot."""
from collections import defaultdict
import csv
from pathlib import Path
from statistics import median


def main():
    waits = defaultdict(list)
    with Path(__file__).with_name("trial_waits.csv").open(encoding="utf-8", newline="") as input_file:
        for record in csv.DictReader(input_file):
            waits[record["method"]].append(int(record["wait_minutes"]))
    for method, minutes in waits.items():
        print(f"{method}: {median(minutes):g} min (n={len(minutes)})")


if __name__ == "__main__":
    main()
