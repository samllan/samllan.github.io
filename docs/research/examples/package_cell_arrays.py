"""Package cell measurements and IDs in one small, aligned archive.

The research used HDF5. This example uses NumPy's portable NPZ format.
"""
from io import BytesIO

import numpy as np


def package_cells(output, cell_ids, coordinates, features):
    ids = np.asarray(cell_ids, dtype=str)
    xy = np.asarray(coordinates, dtype=int)
    vectors = np.asarray(features, dtype=np.float32)
    if ids.ndim != 1 or len(set(ids)) != len(ids) or len(ids) == 0:
        raise ValueError("Provide nonempty, unique cell identifiers")
    if xy.shape != (len(ids), 2) or vectors.ndim != 2 or len(vectors) != len(ids):
        raise ValueError("Each cell needs one coordinate pair and one feature vector")
    if not np.isfinite(vectors).all():
        raise ValueError("Cell features must be finite")
    np.savez_compressed(output, identifiers=ids, xy=xy, features=vectors)


if __name__ == "__main__":
    archive = BytesIO()
    package_cells(archive, ["C1-1", "C1-2"], [[7, 6], [9, 3]], [[0.3], [0.8]])
    archive.seek(0)
    with np.load(archive) as cells:
        print(dict(zip(cells["identifiers"], cells["xy"].tolist())))
