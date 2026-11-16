"""Prepare paired views of each patch for feature-learning experiments."""
import numpy as np


def paired_views(patches, seed):
    random = np.random.default_rng(seed)
    for patch_id, pixels in patches.items():
        pixels = np.asarray(pixels, dtype=float)
        if pixels.ndim != 2:
            raise ValueError("Each example patch must be a grayscale image")
        views = []
        for _ in range(2):
            image = np.flip(pixels, axis=1) if random.integers(2) else pixels
            gain = random.uniform(0.85, 1.15)
            views.append(np.clip(image * gain, 0, 1))
        yield patch_id, views[0], views[1]


if __name__ == "__main__":
    for patch_id, first, second in paired_views({"p1": [[0.1, 0.5], [0.7, 1.0]]}, seed=9):
        print(patch_id, first.round(2).tolist(), second.round(2).tolist())
