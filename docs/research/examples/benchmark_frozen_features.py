"""Compare feature arrays on one fixed held-out split.

The example uses a nearest-centroid classifier and generated feature vectors.
"""
import numpy as np


def benchmark(representations, labels, train_indices, test_indices):
    labels = np.asarray(labels)
    train_indices = np.asarray(train_indices, dtype=int)
    test_indices = np.asarray(test_indices, dtype=int)
    if not len(train_indices) or not len(test_indices) or set(train_indices) & set(test_indices):
        raise ValueError("Provide disjoint, nonempty training and test sets")
    if min(*train_indices, *test_indices) < 0 or max(*train_indices, *test_indices) >= len(labels):
        raise ValueError("Split index out of range")
    classes = np.unique(labels[train_indices])
    scores = {}
    for name, features in representations.items():
        features = np.asarray(features, dtype=float)
        if features.ndim != 2 or len(features) != len(labels):
            raise ValueError(f"Feature and label count differs for {name}")
        centres = np.array([features[train_indices][labels[train_indices] == label].mean(axis=0) for label in classes])
        distances = ((features[test_indices, None] - centres[None]) ** 2).sum(axis=2)
        predicted = classes[distances.argmin(axis=1)]
        scores[name] = float((predicted == labels[test_indices]).mean())
    return scores


if __name__ == "__main__":
    features = {"first": [[0], [4], [0.3], [3.7]], "second": [[0], [4], [3.5], [3.7]]}
    print(benchmark(features, ["a", "b", "a", "b"], [0, 1], [2, 3]))
