"""Run a small held-out classification on pooled patch features.

The demo uses nearest centroids with generated feature arrays.
"""
import numpy as np


def bag_means(bags):
    means = {}
    for sample, patches in bags.items():
        matrix = np.asarray(patches, dtype=float)
        if matrix.ndim != 2 or not len(matrix) or not np.isfinite(matrix).all():
            raise ValueError(f"Invalid patch features for {sample}")
        means[sample] = matrix.mean(axis=0)
    return means


def score_held_out(bags, training_labels):
    if set(training_labels.values()) != {"ABC", "GCB"}:
        raise ValueError("Both subtype labels are required in training")
    features = bag_means(bags)
    centroids = {
        label: np.mean([features[sample] for sample, value in training_labels.items() if value == label], axis=0)
        for label in ("ABC", "GCB")
    }

    scores = {}
    for sample in features.keys() - training_labels.keys():
        vector = features[sample]
        distance_a = float(np.linalg.norm(vector - centroids["ABC"]))
        distance_g = float(np.linalg.norm(vector - centroids["GCB"]))
        scores[sample] = distance_g - distance_a
    return dict(sorted(scores.items()))


if __name__ == "__main__":
    examples = {"a": [[0.1], [0.2]], "b": [[0.9], [0.8]], "c": [[0.6], [0.7], [0.8]]}
    print(score_held_out(examples, {"a": "ABC", "b": "GCB"}))
