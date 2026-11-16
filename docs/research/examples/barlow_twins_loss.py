"""Inspect the Barlow Twins objective on two batches of small feature vectors.

Reference: Zbontar et al. (2021), https://proceedings.mlr.press/v139/zbontar21a.html
"""

import numpy as np


def standardise(columns):
    centred = columns - columns.mean(axis=0)
    scale = np.maximum(centred.std(axis=0), 1e-8)
    return centred / scale


def barlow_twins_loss(first_view, second_view, redundancy_weight=0.005):
    first, second = np.asarray(first_view, dtype=float), np.asarray(second_view, dtype=float)
    if first.shape != second.shape or first.ndim != 2 or first.shape[0] < 2 or first.shape[1] < 1:
        raise ValueError('Provide two equally sized batches with at least two samples and one feature.')
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError('Features must be finite.')
    correlation = standardise(first).T @ standardise(second) / first.shape[0]
    diagonal = np.diag(correlation)
    agreement_loss = np.square(1 - diagonal).sum()
    redundancy_loss = np.square(correlation - np.diag(diagonal)).sum()
    return agreement_loss, redundancy_loss, agreement_loss + redundancy_weight * redundancy_loss


if __name__ == '__main__':
    independent = np.array([[-1, -1], [-1, 1], [1, -1], [1, 1]])
    duplicated = independent[:, [0, 0]]
    for label, features in (('Independent features', independent), ('Duplicated feature', duplicated)):
        agreement, redundancy, total = barlow_twins_loss(features, features)
        print(f'{label:<20} | agreement {agreement:.3f} | redundancy {redundancy:.3f} | total {total:.3f}')
