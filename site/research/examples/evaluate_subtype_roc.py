"""Build a binary ROC curve and compute its area on supplied predictions."""
from itertools import groupby
from math import isfinite


def roc(points, positive_label="ABC"):
    points = list(points)
    labels = {label for label, _ in points}
    if len(labels) != 2 or positive_label not in labels or not all(isfinite(score) for _, score in points):
        raise ValueError("Provide two classes and finite scores")
    positives = sum(label == positive_label for label, _ in points)
    negatives = len(points) - positives
    true_positive = false_positive = 0
    curve = [(0.0, 0.0)]
    ranked = sorted(points, key=lambda example: -example[1])
    for _, tied in groupby(ranked, key=lambda example: example[1]):
        for label, _ in tied:
            true_positive += label == positive_label
            false_positive += label != positive_label
        curve.append((false_positive / negatives, true_positive / positives))
    area = sum((x2 - x1) * (y1 + y2) / 2 for (x1, y1), (x2, y2) in zip(curve, curve[1:]))
    return curve, area


if __name__ == "__main__":
    print(roc([("ABC", 0.9), ("GCB", 0.6), ("ABC", 0.6), ("GCB", 0.2)]))
