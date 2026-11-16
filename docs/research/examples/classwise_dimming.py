"""Demonstrate class-specific dimming with a tiny, inspectable linear model."""


def classwise_dimming(regions, weights, *, step=0.25, iterations=20):
    """Fit one mask per class while leaving the model and the original input fixed."""
    for class_weights in weights:
        contributions = [region * weight for region, weight in zip(regions, class_weights)]
        before = sum(contributions)
        mask = [1.0] * len(regions)
        for _ in range(iterations):
            mask = [max(0.0, min(1.0, value + step * gradient))
                    for value, gradient in zip(mask, contributions)]
        after = sum(value * contribution for value, contribution in zip(mask, contributions))
        yield before, after, mask


if __name__ == '__main__':
    # Four toy regions and two classes with deliberately different scoring rules.
    regions = (0.8, 0.6, 0.9, 0.4)
    weights = ((1.0, -1.0, 0.4, -0.8), (-0.4, 1.0, -0.7, 0.9))
    for label, (before, after, mask) in zip(('A', 'B'), classwise_dimming(regions, weights)):
        print(f'Class {label} | score {before:.2f} -> {after:.2f} | mask {[round(value, 2) for value in mask]}')
