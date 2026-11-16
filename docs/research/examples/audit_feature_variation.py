"""Check feature arrays for constant and nearly duplicate columns."""
import numpy as np


def audit_features(features, tolerance=1e-8, correlation_threshold=0.99):
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or len(matrix) < 2 or not np.isfinite(matrix).all():
        raise ValueError("Provide a finite sample-by-feature matrix")
    centred = matrix - matrix.mean(axis=0)
    spread = centred.std(axis=0)
    variable = np.flatnonzero(spread > tolerance)
    normalised = centred[:, variable] / spread[variable]
    correlation = normalised.T @ normalised / len(matrix)
    duplicate_indices = np.argwhere(np.triu(np.abs(correlation) >= correlation_threshold, k=1))
    return np.flatnonzero(spread <= tolerance).tolist(), [
        (int(variable[i]), int(variable[j])) for i, j in duplicate_indices
    ]


if __name__ == "__main__":
    print(audit_features([[1, 0, 5], [2, 0, 10], [3, 0, 15]]))
