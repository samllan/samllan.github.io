"""Preserve the location of each segmented cell when assembling a dataset."""


def index_cells(core_origins, detections):
    seen = set()
    for core_id, cell_id, local_x, local_y in detections:
        key = (core_id, cell_id)
        if key in seen or min(local_x, local_y) < 0:
            raise ValueError(f"Duplicate cell or negative coordinate: {key}")
        seen.add(key)
        origin_x, origin_y = core_origins[core_id]
        yield {
            "core": core_id, "cell": cell_id,
            "scan_x": origin_x + local_x, "scan_y": origin_y + local_y,
        }


if __name__ == "__main__":
    for row in index_cells({"C1": (640, 480)}, [("C1", 1, 29, 18), ("C1", 2, 61, 70)]):
        print(row)
