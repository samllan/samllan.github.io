"""Compare patch occlusion and repetition with a fixed bag scorer."""
from typing import NamedTuple

import numpy as np


class PatchResponse(NamedTuple):
    patch: int
    occlusion_delta: np.ndarray
    repetition_delta: np.ndarray


def compare_perturbations(bag, score):
    bag = np.asarray(bag, dtype=float)
    if bag.ndim != 2 or len(bag) < 2 or not np.isfinite(bag).all():
        raise ValueError("Provide at least two patches with finite features")

    def class_scores(patches):
        return np.asarray(score(patches), dtype=float)

    baseline = class_scores(bag)
    if baseline.ndim != 1 or not baseline.size or not np.isfinite(baseline).all():
        raise ValueError("The scorer must return one finite score per class")
    for patch in range(len(bag)):
        removed = class_scores(np.delete(bag, patch, axis=0))
        repeated = class_scores(np.repeat(bag[patch:patch + 1], len(bag), axis=0))
        if any(value.shape != baseline.shape or not np.isfinite(value).all() for value in (removed, repeated)):
            raise ValueError("Perturbed bags must return the same class scores")
        yield PatchResponse(patch, removed - baseline, repeated - baseline)


if __name__ == "__main__":
    patches = [[0.1, 0.9], [0.2, 0.6], [0.8, 0.1]]
    for patch, removed, repeated in compare_perturbations(patches, lambda bag: bag.mean(axis=0)):
        print(f"Patch {patch}: remove {removed.round(3)}, repeat {repeated.round(3)}")
