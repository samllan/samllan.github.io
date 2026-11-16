"""Fit a brightness mask for each class using one fixed scoring model.

Start with every region at full brightness. Dimming a region can raise a
class score if that region had been suppressing it. The example uses four
invented regions and a linear scoring rule to show how the masks differ.
"""

from math import isfinite
from typing import NamedTuple


class Explanation(NamedTuple):
    baseline_score: float
    masked_score: float
    brightness: tuple[float, ...]


def fit_class_mask(regions, score_and_gradient, *, step_size=0.25, steps=20):
    """Optimise a bounded mask using a score and its input gradient."""
    regions = tuple(regions)
    if not regions or not isfinite(step_size) or step_size <= 0 or steps < 1:
        raise ValueError("Provide regions, a positive step size and at least one step.")

    original = (1.0,) * len(regions)
    baseline, gradient = score_and_gradient(regions)
    brightness = original
    score = baseline
    for _ in range(steps):
        if len(gradient) != len(regions):
            raise ValueError("The model must return one gradient value per region.")

        # For a masked value x * b, the gradient with respect to b is x times
        # the model's input gradient. The model stays fixed while b changes.
        brightness = tuple(
            min(1.0, max(0.0, value + step_size * region * direction))
            for value, region, direction in zip(brightness, regions, gradient)
        )
        masked = tuple(value * region for value, region in zip(brightness, regions))
        score, gradient = score_and_gradient(masked)

    if score < baseline:
        return Explanation(baseline, baseline, original)
    return Explanation(baseline, score, brightness)


if __name__ == "__main__":
    from functools import partial

    def linear_score(values, *, weights):
        return sum(value * weight for value, weight in zip(values, weights)), weights

    regions = (0.8, 0.6, 0.9, 0.4)
    class_weights = {"A": (1.0, -1.0, 0.4, -0.8), "B": (-0.4, 1.0, -0.7, 0.9)}

    for label, weights in class_weights.items():
        result = fit_class_mask(regions, partial(linear_score, weights=weights))
        mask = " ".join(f"{value:.2f}" for value in result.brightness)
        print(f"Class {label}: {result.baseline_score:.2f} -> {result.masked_score:.2f} | {mask}")
