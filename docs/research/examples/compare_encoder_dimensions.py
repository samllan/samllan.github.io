"""Compare the dimensions and recorded size of cached feature arrays."""
import numpy as np


def describe_caches(caches):
    sample_counts = {len(cache) for cache in caches.values()}
    if len(sample_counts) > 1 or any(cache.ndim != 2 for cache in caches.values()):
        raise ValueError("Compare one two-dimensional feature array per encoder on the same sample count")
    return [
        (encoder, array.shape[0], array.shape[1], str(array.dtype), array.nbytes)
        for encoder, array in caches.items()
    ]


if __name__ == "__main__":
    caches = {"small": np.zeros((30, 16), dtype=np.float32), "wide": np.zeros((30, 64), dtype=np.float32)}
    print("encoder,examples,features,dtype,bytes")
    for row in describe_caches(caches):
        print(*row, sep=",")
