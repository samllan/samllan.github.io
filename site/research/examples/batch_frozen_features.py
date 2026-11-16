"""Extract features in batches while preserving the order of patch IDs.

A fixed summary function stands in for a pretrained image encoder in the demo.
"""
import numpy as np


def extract_features(samples, encoder, batch_size):
    if batch_size < 1:
        raise ValueError("Batch size must be positive")
    if len({name for name, _ in samples}) != len(samples):
        raise ValueError("Patch IDs must be unique")
    for start in range(0, len(samples), batch_size):
        batch = samples[start:start + batch_size]
        pixels = np.asarray([image for _, image in batch])
        vectors = np.asarray(encoder(pixels))
        if vectors.ndim != 2 or len(vectors) != len(batch):
            raise ValueError("Encoder must return one vector per patch")
        yield from ((name, vector) for (name, _), vector in zip(batch, vectors))


def intensity_features(batch):
    pixels = batch.reshape(len(batch), -1)
    return np.column_stack((pixels.mean(axis=1), pixels.std(axis=1)))


if __name__ == "__main__":
    samples = [("p1", [[0.1, 0.4]]), ("p2", [[0.7, 0.9]]), ("p3", [[0.4, 0.2]])]
    print([(name, vector.round(3).tolist()) for name, vector in extract_features(samples, intensity_features, 2)])
