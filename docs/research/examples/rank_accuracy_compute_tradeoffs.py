"""Find models that are undominated on accuracy, runtime and memory."""
from math import isfinite


def efficient_models(measurements):
    if any(
        not all(map(isfinite, (accuracy, seconds, memory)))
        or not 0 <= accuracy <= 1 or min(seconds, memory) <= 0
        for accuracy, seconds, memory in measurements.values()
    ):
        raise ValueError("Provide valid accuracies and positive resource measurements")
    costs = {name: (1 - accuracy, seconds, memory) for name, (accuracy, seconds, memory) in measurements.items()}

    def dominates(first, second):
        return first != second and all(a <= b for a, b in zip(first, second))

    return [name for name, vector in costs.items() if not any(dominates(other, vector) for other in costs.values())]


if __name__ == "__main__":
    print(efficient_models({"wide": (0.93, 40, 900), "small": (0.91, 21, 600), "slow": (0.90, 53, 950)}))
