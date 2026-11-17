"""Inspect the two parts of a variational autoencoder objective.

This example uses standard binary cross-entropy and a diagonal Gaussian
posterior. The thesis also explored more specialised reconstruction losses.
"""
from typing import NamedTuple

import numpy as np


class Loss(NamedTuple):
    reconstruction: float
    regularisation: float
    total: float


def score_vae(pixels, decoded, mean, log_variance, beta=1.0):
    pixels, decoded, mean, log_variance = (
        np.asarray(value, dtype=float) for value in (pixels, decoded, mean, log_variance)
    )
    if pixels.ndim != 2 or not pixels.size or decoded.shape != pixels.shape:
        raise ValueError("Provide aligned sample-by-pixel matrices")
    if not mean.size or mean.ndim != 2 or mean.shape != log_variance.shape or len(mean) != len(pixels):
        raise ValueError("Provide one latent mean and log variance per sample")
    if not all(np.isfinite(value).all() for value in (pixels, decoded, mean, log_variance)):
        raise ValueError("Inputs must be finite")
    if min(pixels.min(), decoded.min()) < 0 or max(pixels.max(), decoded.max()) > 1:
        raise ValueError("Pixel values and decoder probabilities must be between zero and one")
    if not np.isfinite(beta) or beta < 0:
        raise ValueError("The regularisation weight must be finite and nonnegative")

    probability = np.clip(decoded, 1e-8, 1 - 1e-8)
    reconstruction = -(pixels * np.log(probability) + (1 - pixels) * np.log1p(-probability))
    with np.errstate(over="ignore"):
        gaussian_kl = 0.5 * (np.expm1(log_variance) + mean**2 - log_variance)
    if not np.isfinite(gaussian_kl).all():
        raise ValueError("Latent parameters are outside the supported numeric range")
    reconstruction = float(reconstruction.sum(axis=1).mean())
    regularisation = float(gaussian_kl.sum(axis=1).mean())
    return Loss(reconstruction, regularisation, reconstruction + beta * regularisation)


if __name__ == "__main__":
    loss = score_vae([[0, 1], [1, 0]], [[0.2, 0.9], [0.8, 0.2]], [[0.4], [-0.4]], [[0.1], [0.1]], beta=0.5)
    print(f"Reconstruction {loss.reconstruction:.3f} | KL {loss.regularisation:.3f} | total {loss.total:.3f}")
