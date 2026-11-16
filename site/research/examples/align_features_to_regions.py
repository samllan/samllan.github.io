"""Match coordinates and feature rows by ID before building model inputs."""


def align_features(regions, vectors):
    missing = regions.keys() - vectors.keys()
    extra = vectors.keys() - regions.keys()
    if missing or extra:
        raise ValueError(f"Missing vectors: {sorted(missing)}. Unknown vectors: {sorted(extra)}")
    return [(region_id, regions[region_id], vectors[region_id]) for region_id in regions]


if __name__ == "__main__":
    regions = {"A": (12, 6), "B": (80, 5)}
    vectors = {"B": (0.1, 0.2), "A": (0.3, 0.4)}
    for region_id, (x, y), vector in align_features(regions, vectors):
        print(region_id, x, y, *vector, sep=",")
