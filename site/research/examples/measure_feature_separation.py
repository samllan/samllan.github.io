"""Measure how well given groups separate in a small feature matrix."""
import numpy as np


def silhouette_scores(features, groups):
    features = np.asarray(features, dtype=float)
    groups = np.asarray(groups)
    categories = np.unique(groups)
    if features.ndim != 2 or len(features) != len(groups) or len(categories) < 2:
        raise ValueError("Provide a feature vector and group per example, with at least two groups")
    distances = np.linalg.norm(features[:, None] - features[None, :], axis=2)
    scores = []
    for index, group in enumerate(groups):
        same = groups == group
        same[index] = False
        if not same.any():
            scores.append(0.0)
            continue
        within = distances[index, same].mean()
        nearest_other = min(distances[index, groups == other].mean() for other in categories if other != group)
        scale = max(within, nearest_other)
        scores.append(float((nearest_other - within) / scale) if scale else 0.0)
    return scores


if __name__ == "__main__":
    scores = silhouette_scores([[0.0], [0.5], [3.5], [4.0]], ["g1", "g1", "g2", "g2"])
    print([round(score, 2) for score in scores])
