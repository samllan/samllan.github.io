"""Fit a small shared encoder with the Barlow Twins objective.

Numerical gradients keep this small demonstration focused on the objective.
These would be too expensive for the image networks used in the thesis.
"""
import numpy as np

from learn_image_features import feature_loss


def fit_encoder(first, second, initial, *, steps=40, learning_rate=0.3):
    first, second, weights = (
        np.array(value, dtype=float, copy=True) for value in (first, second, initial)
    )
    if first.ndim != 2 or first.shape != second.shape or weights.ndim != 2 or first.shape[1] != len(weights):
        raise ValueError("Provide aligned inputs and a shared linear weight matrix")
    if steps < 1 or not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("Use positive steps and a finite learning rate")

    def objective(matrix):
        return feature_loss(first, second, lambda views: views @ matrix, redundancy_weight=0.1).total

    history = [objective(weights)]
    epsilon = 1e-5
    for _ in range(steps):
        gradient = np.zeros_like(weights)
        for index in np.ndindex(weights.shape):
            offsets = np.zeros_like(weights)
            offsets[index] = epsilon
            gradient[index] = (objective(weights + offsets) - objective(weights - offsets)) / (2 * epsilon)
        proposal = weights - learning_rate * gradient
        loss = objective(proposal)
        if loss < history[-1]:
            weights = proposal
        history.append(min(history[-1], loss))
    return weights, history


if __name__ == "__main__":
    signal = np.array([[-2, -1], [-2, 1], [2, -1], [2, 1]], dtype=float)
    second = signal * [0.8, 1.1] + [0.1, -0.3]
    weights, loss = fit_encoder(signal, second, [[1.0, 1.0], [0.15, -0.15]])
    print(f"Objective: {loss[0]:.4f} to {loss[-1]:.4f}")
    print("Shared weights:", weights.round(3).tolist())
