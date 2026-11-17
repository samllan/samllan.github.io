"""Compare flat and hierarchical pooling on the same cells.

Mean pooling makes the effect of hierarchy visible: a flat mean weights
every cell equally, while a hierarchical mean gives each valid patch a vote.
"""
import numpy as np


def compare_pooling(cells, mask):
    cells = np.asarray(cells, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    if cells.ndim != 3 or mask.shape != cells.shape[:2]:
        raise ValueError("Expected patch-by-cell features and a matching mask")
    if not mask.any():
        zero = np.zeros(cells.shape[-1])
        return {"flat": zero, "hierarchical": zero.copy()}

    flat = cells[mask].mean(axis=0)
    patch_vectors = [features[valid].mean(axis=0) for features, valid in zip(cells, mask) if valid.any()]
    return {"flat": flat, "hierarchical": np.mean(patch_vectors, axis=0)}


if __name__ == "__main__":
    features = [[[0], [0], [0]], [[1], [999], [999]], [[999], [999], [999]]]
    mask = [[True, True, True], [True, False, False], [False, False, False]]
    for variant, result in compare_pooling(features, mask).items():
        print(f"{variant}: {result[0]:.2f}")
