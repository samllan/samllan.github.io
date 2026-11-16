"""Measure the agreement and redundancy of features from two views.

Pass two aligned batches through the same encoder. The example uses small
arrays as stand-ins for encoded images and evaluates the loss with NumPy.

Method: Zbontar et al., Barlow Twins (ICML 2021).
https://proceedings.mlr.press/v139/zbontar21a.html
"""

from typing import NamedTuple

import numpy as np


class FeatureLoss(NamedTuple):
    agreement: float
    redundancy: float
    total: float


def standardise_features(features):
    centred = features - features.mean(axis=0)
    return centred / np.maximum(centred.std(axis=0), 1e-8)


def feature_loss(first_view, second_view, encode, *, redundancy_weight=0.005):
    """Measure the Barlow Twins objective using one shared encoder."""
    first = np.asarray(encode(first_view), dtype=float)
    second = np.asarray(encode(second_view), dtype=float)
    if first.ndim != 2 or first.shape != second.shape:
        raise ValueError("The encoder must return matching sample-by-feature batches.")
    if first.shape[0] < 2 or first.shape[1] == 0:
        raise ValueError("Use at least two samples and one feature.")
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError("Encoded features must be finite.")
    if not np.isfinite(redundancy_weight) or redundancy_weight < 0:
        raise ValueError("The redundancy weight must be finite and nonnegative.")

    correlation = standardise_features(first).T @ standardise_features(second) / len(first)
    diagonal = np.diag(correlation)

    # Each diagonal entry compares a feature with itself across both views.
    agreement = float(np.square(1 - diagonal).sum())

    # Off-diagonal entries reveal when distinct features carry the same signal.
    redundancy = float(np.square(correlation - np.diag(diagonal)).sum())
    return FeatureLoss(agreement, redundancy, agreement + redundancy_weight * redundancy)


if __name__ == "__main__":
    independent = np.array([[-1, -1], [-1, 1], [1, -1], [1, 1]])
    duplicated = independent[:, [0, 0]]
    for label, batch in (("Independent features", independent), ("Duplicated feature", duplicated)):
        loss = feature_loss(batch, 2 * batch + 1, encode=np.asarray)
        print(f"{label} | agreement loss {loss.agreement:.3f} | total loss {loss.total:.3f}")
