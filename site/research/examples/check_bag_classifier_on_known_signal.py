"""Check a bag score on a task where the source of the label is known.

Each positive bag contains one marked instance. Negative bags contain none.
The data are synthetic, as a small analogue of the CIFAR bag experiment.
"""
import numpy as np

from evaluate_subtype_roc import roc


def make_benchmark(rng, examples_per_class, instances):
    if examples_per_class < 1 or instances < 2:
        raise ValueError("Use a positive class size and at least two instances per bag")
    bags = rng.normal(0, 1, size=(2 * examples_per_class, instances))
    for bag in bags[examples_per_class:]:
        bag[rng.integers(instances)] += 5
    labels = ["negative"] * examples_per_class + ["positive"] * examples_per_class
    return bags, labels


if __name__ == "__main__":
    bags, labels = make_benchmark(np.random.default_rng(17), examples_per_class=32, instances=12)
    for name, scores in (("mean", bags.mean(axis=1)), ("maximum", bags.max(axis=1))):
        _, auc = roc(zip(labels, scores), positive_label="positive")
        print(f"{name}: area under ROC {auc:.3f}")
