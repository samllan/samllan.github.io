"""Summarise recorded predictions by validation fold.

Report mean absolute error for grading and accuracy for subtype prediction.
The two examples use independent sets of invented predictions.
"""

from collections import defaultdict
from math import isfinite
from statistics import mean


def grading_error_by_fold(predictions):
    """Take (fold, reference score, predicted score) records."""
    errors = defaultdict(list)
    for fold, reference, predicted in predictions:
        if not isfinite(reference) or not isfinite(predicted):
            raise ValueError("Grading scores must be finite.")
        errors[fold].append(abs(reference - predicted))
    return {fold: mean(errors[fold]) for fold in sorted(errors)}


def subtype_accuracy_by_fold(predictions):
    """Take (fold, reference label, predicted label) records."""
    matches = defaultdict(list)
    for fold, reference, predicted in predictions:
        matches[fold].append(reference == predicted)
    # Report each fold separately so a pooled result cannot hide a weak fold.
    return {fold: mean(matches[fold]) for fold in sorted(matches)}


if __name__ == "__main__":
    grades = [(0, 2, 2.4), (0, 1, 0.9), (1, 3, 2.6), (1, 1, 1.2)]
    subtypes = [(0, "A", "A"), (0, "B", "B"), (1, "A", "B"), (1, "B", "B")]

    print("Grading | mean absolute error")
    for fold, error in grading_error_by_fold(grades).items():
        print(f"Fold {fold:d}  | {error:.2f}")

    print("\nSubtype | accuracy")
    for fold, accuracy in subtype_accuracy_by_fold(subtypes).items():
        print(f"Fold {fold:d}  | {accuracy:.0%}")
