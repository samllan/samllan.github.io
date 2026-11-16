"""Describe the scores plotted inside a supplied region of interest."""
import numpy as np


def describe_overlay(scores, region):
    scores = np.asarray(scores, dtype=float)
    region = np.asarray(region, dtype=bool)
    if region.shape != scores.shape or not region.any():
        raise ValueError("Supply a nonempty region aligned to the scores")
    observed = scores[region & np.isfinite(scores)]
    return {
        "coverage": len(observed) / int(region.sum()),
        "median": float(np.median(observed)) if len(observed) else None,
        "range": (float(observed.min()), float(observed.max())) if len(observed) else None,
    }


if __name__ == "__main__":
    print(describe_overlay([[0.4, np.nan], [0.8, 0.5]], [[True, True], [True, False]]))
