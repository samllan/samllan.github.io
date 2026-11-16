"""Estimate raw storage for image patches and feature vectors.

Compare both representations on the same number of regions. Estimates use
uncompressed pixel and feature values and omit container overhead.
"""

from typing import NamedTuple


class StorageEstimate(NamedTuple):
    bytes_per_region: int
    total_bytes: int


def estimate_storage(region_count, patch_size, vector_length, *, bytes_per_feature=4):
    """Compare 8-bit RGB patches with fixed-length feature vectors."""
    width, height = patch_size
    if min(region_count, width, height, vector_length, bytes_per_feature) <= 0:
        raise ValueError("Counts, dimensions and feature sizes must be positive.")

    # An RGB pixel has three one-byte channels. Each vector element has the
    # supplied precision, which defaults to four bytes for float32.
    rgb_bytes = width * height * 3
    feature_bytes = vector_length * bytes_per_feature
    return {
        "RGB patches": StorageEstimate(rgb_bytes, region_count * rgb_bytes),
        "Feature vectors": StorageEstimate(feature_bytes, region_count * feature_bytes),
    }


if __name__ == "__main__":
    count = 500
    patch_size = (224, 224)
    vector_length = 256
    print(f"{count} regions of {patch_size[0]} x {patch_size[1]} pixels, {vector_length} features per vector")
    print(f"{'Representation':<18}{'Bytes per region':>18}{'Total bytes':>16}")
    for name, estimate in estimate_storage(count, patch_size, vector_length).items():
        print(f"{name:<18}{estimate.bytes_per_region:>18,}{estimate.total_bytes:>16,}")
