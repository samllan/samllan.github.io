"""Fit a small PCA projection and apply the same basis to new examples."""
import numpy as np


def fit_projection(features, components=2):
    values = np.asarray(features, dtype=float)
    if values.ndim != 2 or not 1 <= components <= min(values.shape):
        raise ValueError("Choose a valid number of components for the feature matrix")
    centre = values.mean(axis=0)
    _, singular, basis = np.linalg.svd(values - centre, full_matrices=False)
    variance = singular**2
    proportion = variance[:components] / variance.sum() if variance.sum() else np.zeros(components)
    return centre, basis[:components], proportion


if __name__ == "__main__":
    features = np.array([[0.1, 0.3, 0.2], [0.2, 0.45, 0.17], [0.75, 0.6, 0.9]])
    centre, basis, proportion = fit_projection(features)
    print("coordinates", ((features - centre) @ basis.T).round(3).tolist())
    print("variance explained", proportion.round(3).tolist())
