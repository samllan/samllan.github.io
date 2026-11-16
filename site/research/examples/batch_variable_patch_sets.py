"""Batch similarly sized patch collections to reduce padded positions."""


def batch_patch_sets(patch_counts, batch_size):
    if batch_size < 1 or any(count < 1 for count in patch_counts.values()):
        raise ValueError("Batch size and patch counts must be positive")
    ordered = sorted(patch_counts, key=lambda name: (patch_counts[name], name))
    for start in range(0, len(ordered), batch_size):
        batch = ordered[start:start + batch_size]
        counts = [patch_counts[name] for name in batch]
        padded_slots = len(batch) * max(counts) - sum(counts)
        yield batch, padded_slots


if __name__ == "__main__":
    print(list(batch_patch_sets({"a": 12, "b": 3, "c": 5, "d": 15}, batch_size=2)))
