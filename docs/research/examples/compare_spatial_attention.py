"""Compare patch attention with and without two-dimensional rotary positions.

One attention head and generated arrays keep the ablation visible.
The module also ignores padded keys and handles bags without valid patches.
"""
import numpy as np


def rotate_axes(vectors, coordinates):
    width = vectors.shape[-1]
    if not width or width % 4:
        raise ValueError("Use a head width divisible by four for two spatial axes")
    quarter = width // 4
    frequencies = 10000 ** (-np.arange(quarter) / quarter)
    angles = coordinates[..., :, None] * frequencies
    pairs = vectors.reshape(*vectors.shape[:-1], 2, quarter, 2)
    cosine, sine = np.cos(angles), np.sin(angles)
    even, odd = pairs[..., 0], pairs[..., 1]
    return np.stack((cosine * even - sine * odd, sine * even + cosine * odd), axis=-1).reshape(vectors.shape)


def pool_attention(query, keys, values, positions, valid, *, positional=False):
    query, keys, values, positions = (np.asarray(x, dtype=float) for x in (query, keys, values, positions))
    valid = np.asarray(valid, dtype=bool)
    if query.ndim != 1 or keys.ndim != 2 or not query.size or keys.shape[1] != query.size:
        raise ValueError("Keys and query must share the head width")
    if values.ndim != 2 or len(values) != len(keys) or positions.shape != (len(keys), 2) or valid.shape != (len(keys),):
        raise ValueError("Each key needs one value, coordinate and validity flag")
    if not valid.any():
        return np.zeros(values.shape[1])
    keys, values, positions = keys[valid], values[valid], positions[valid]
    if positional:
        keys = rotate_axes(keys, positions)
    scores = keys @ query / np.sqrt(query.size)
    weights = np.exp(scores - scores.max())
    return (weights / weights.sum()) @ values


if __name__ == "__main__":
    query = [1, 0, 1, 0]
    keys = [[1, 0, 1, 0], [1, 0, 1, 0], [10, 10, 10, 10]]
    values = [[0.2], [0.8], [100]]
    positions = [[0, 0], [2, 1], [3, 1]]
    for positional in (False, True):
        result = pool_attention(query, keys, values, positions, [True, True, False], positional=positional)
        print(f"Positions {positional}: pooled score {result[0]:.3f}")
