"""Probe a fixed grading model with Gaussian noise at its input boundary.

The demo uses a simple scoring function and generated signal bags.
The null class has its own index, separate from the real grade classes.
"""
from typing import NamedTuple

import numpy as np


class Response(NamedTuple):
    median_null_probability: float
    null_calls: int
    bags: int


def probe_null_response(model, signal_bags, *, null_class, seed):
    bags = np.asarray(signal_bags, dtype=float)
    if bags.ndim < 2 or not bags.size or not np.isfinite(bags).all():
        raise ValueError("Provide a finite batch of nonempty bags")
    noise = np.random.default_rng(seed).normal(size=bags.shape)
    combined = np.concatenate((bags, noise), axis=0)
    scores = np.asarray(model(combined), dtype=float)
    if scores.ndim != 2 or len(scores) != len(combined) or not 0 <= null_class < scores.shape[1]:
        raise ValueError("Return one score per bag and class")
    if not np.isfinite(scores).all():
        raise ValueError("Model scores must be finite")
    mass = np.exp(scores - scores.max(axis=1, keepdims=True))
    probabilities = mass / mass.sum(axis=1, keepdims=True)

    def summarise(rows):
        return Response(float(np.median(rows[:, null_class])), int((rows.argmax(axis=1) == null_class).sum()), len(rows))

    return {"signal": summarise(probabilities[:len(bags)]), "noise": summarise(probabilities[len(bags):])}


if __name__ == "__main__":
    signal = np.random.default_rng(3).normal(1.5, 0.4, size=(12, 20, 2))

    def score(bags):
        mean = bags.mean(axis=(1, 2))
        return np.column_stack((mean * 2, mean, 1.5 - mean * 2))

    for kind, response in probe_null_response(score, signal, null_class=2, seed=19).items():
        print(f"{kind}: median null {response[0]:.3f}, {response[1]}/{response[2]} null calls")
