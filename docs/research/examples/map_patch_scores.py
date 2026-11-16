"""Put scored patches back into the coordinate system of an image."""
import numpy as np


def score_grid(image_size, patches):
    width, height = image_size
    sums = np.zeros((height, width))
    hits = np.zeros((height, width), dtype=int)
    for left, top, right, bottom, score in patches:
        if not (0 <= left < right <= width and 0 <= top < bottom <= height) or not np.isfinite(score):
            raise ValueError("Patch bounds and score must be valid")
        sums[top:bottom, left:right] += score
        hits[top:bottom, left:right] += 1
    return np.divide(sums, hits, where=hits > 0, out=np.full(sums.shape, np.nan))


if __name__ == "__main__":
    print(score_grid((4, 3), [(0, 0, 3, 2, 0.4), (2, 1, 4, 3, 0.8)]))
