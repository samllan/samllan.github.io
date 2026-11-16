"""Demonstrate the reconstruction task with a linear autoencoder.

SVD gives the optimum for this small linear example. The thesis also trained
nonlinear models. Keep the fitted mean and basis with the latent codes.
"""
import numpy as np


def fit_linear_autoencoder(patches, dimensions):
    patches = np.asarray(patches, dtype=float)
    if patches.ndim != 2 or not 1 <= dimensions <= min(patches.shape):
        raise ValueError("Choose a valid bottleneck for a sample-by-feature matrix")
    centre = patches.mean(axis=0)
    _, _, components = np.linalg.svd(patches - centre, full_matrices=False)
    return centre, components[:dimensions]


def encode(patches, centre, basis):
    return (np.asarray(patches) - centre) @ basis.T


def decode(codes, centre, basis):
    return np.asarray(codes) @ basis + centre


if __name__ == "__main__":
    patches = [[0.1, 0.2, 0.3], [0.6, 0.9, 0.8], [0.8, 0.2, 0.4]]
    centre, basis = fit_linear_autoencoder(patches, 2)
    codes = encode(patches, centre, basis)
    print(codes.round(3))
