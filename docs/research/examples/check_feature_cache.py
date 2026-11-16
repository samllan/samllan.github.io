"""Validate cached features against the metadata a later experiment expects."""
import numpy as np


def check_cache(vectors, ids, encoder, *, expected_ids, expected_encoder, width):
    issues = []
    expected_ids = tuple(expected_ids)
    if tuple(ids) != expected_ids:
        issues.append("region IDs or ordering changed")
    if encoder != expected_encoder:
        issues.append("encoder changed")
    if np.shape(vectors) != (len(expected_ids), width):
        issues.append("vector shape changed")
    return issues


if __name__ == "__main__":
    example = np.zeros((2, 8))
    print(check_cache(example, ["B", "A"], "encoder-v1", expected_ids=["A", "B"], expected_encoder="encoder-v2", width=8))
