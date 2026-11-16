"""Write one feature vector per region while preserving its source coordinates.

Pass vectors in the order in which the regions were encoded. This example
uses two generated vectors and writes their CSV to the terminal.
"""

import csv
from math import isfinite
from sys import stdout

from prepare_image_regions import grid_patches


def write_feature_table(regions, vectors, output):
    """Write matched region records and fixed-length vectors to a text stream."""
    if len(regions) != len(vectors) or not regions:
        raise ValueError("Supply the same nonzero number of regions and vectors.")

    labels = {region.label for region in regions}
    width = len(vectors[0])
    if len(labels) != len(regions):
        raise ValueError("Region labels must be unique.")
    if not width or any(len(vector) != width for vector in vectors):
        raise ValueError("Use nonempty vectors of the same length.")
    if any(not isfinite(value) for vector in vectors for value in vector):
        raise ValueError("Feature values must be finite.")

    writer = csv.writer(output, lineterminator="\n")
    feature_names = [f"feature_{number}" for number in range(1, width + 1)]
    writer.writerow(["region_id", "left", "top", "right", "bottom", *feature_names])
    # Store the coordinates with the vector so the association survives sorting.
    for region, vector in zip(regions, vectors):
        writer.writerow([region.label, *region.bounds, *vector])


if __name__ == "__main__":
    regions = list(grid_patches((8, 4), size=4, stride=4))
    vectors = [(0.12, 0.68), (0.43, 0.19)]
    write_feature_table(regions, vectors, stdout)
