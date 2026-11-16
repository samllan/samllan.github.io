"""Count saved patches per core, including cores with zero matches."""
from collections import Counter


def count_patches(core_ids, patch_records):
    core_ids = tuple(core_ids)
    counts = Counter(dict.fromkeys(core_ids, 0))
    if len(counts) != len(core_ids):
        raise ValueError("Core identifiers must be unique")
    seen = set()
    for core_id, patch_id in patch_records:
        if core_id not in counts or (core_id, patch_id) in seen:
            raise ValueError(f"Unknown core or duplicate patch: {core_id}/{patch_id}")
        seen.add((core_id, patch_id))
        counts[core_id] += 1
    return dict(counts)


if __name__ == "__main__":
    core_ids = ["A", "B", "C"]
    records = [("A", "x0-y0"), ("A", "x16-y0"), ("C", "x0-y0")]
    for core_id, count in count_patches(core_ids, records).items():
        print(core_id, count)
