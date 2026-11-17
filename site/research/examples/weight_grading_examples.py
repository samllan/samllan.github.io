"""Compute the hybrid sampling weights from Appendix A, Algorithm 3."""
from collections import Counter
from math import fsum, isfinite


def probabilities(weights):
    values = tuple(weights)
    if not values or any(not isfinite(value) or value < 0 for value in values):
        raise ValueError("Use finite, nonnegative weights")
    total = fsum(values)
    return [value / total for value in values] if total else [1 / len(values)] * len(values)


def hybrid_weights(labels, losses, previous=None):
    labels, losses = tuple(labels), tuple(losses)
    if not labels or len(labels) != len(losses):
        raise ValueError("Provide one loss per labelled example")
    if any(not isfinite(loss) or loss < 0 for loss in losses):
        raise ValueError("Losses must be finite and nonnegative")
    counts = Counter(labels)
    class_weight = probabilities(1 / counts[label] for label in labels)
    uniform_shift = 0.15 * fsum(losses) / len(losses)
    loss_weight = probabilities(loss + uniform_shift for loss in losses)
    if previous is None:
        return [0.6 * balance + 0.4 * error for balance, error in zip(class_weight, loss_weight)]

    old_weight = probabilities(previous)
    if len(old_weight) != len(labels):
        raise ValueError("Previous weights must follow the same sample order")
    return [
        0.4 * balance + 0.3 * old + 0.3 * error
        for balance, old, error in zip(class_weight, old_weight, loss_weight)
    ]


if __name__ == "__main__":
    labels = [0, 0, 0, 1]
    losses = [0.1, 0.9, 0.1, 0.4]
    initial = hybrid_weights(labels, losses)
    print("Initial:", [round(weight, 3) for weight in initial])
    updated = hybrid_weights(labels, [0.2, 0.6, 0.2, 0.3], previous=initial)
    print("Next epoch:", [round(weight, 3) for weight in updated])
