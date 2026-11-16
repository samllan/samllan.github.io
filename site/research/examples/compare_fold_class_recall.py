"""Report class recall per fold with the denominator beside every score."""
from collections import Counter


def class_recall(rows):
    totals, correct = Counter(), Counter()
    for fold, reference, prediction in rows:
        key = (fold, reference)
        totals[key] += 1
        correct[key] += reference == prediction
    return [(fold, label, n, correct[fold, label] / n) for (fold, label), n in sorted(totals.items())]


if __name__ == "__main__":
    examples = [(0, "ABC", "ABC"), (0, "GCB", "ABC"), (1, "ABC", "GCB"), (1, "GCB", "GCB")]
    for row in class_recall(examples):
        print(*row, sep=",")
