"""Build generated bags with the label rule used in the PCam archive.

A positive bag contains at least one positive patch. Preserve patch IDs so
the same manifest can feed different encoder and classifier comparisons.
"""
from random import Random


def make_bags(labels, *, count_per_class, bag_size, positive_patches, seed):
    if count_per_class < 1 or not 1 <= positive_patches <= bag_size:
        raise ValueError("Use a positive bag count and a valid positive patch count")
    if any(label not in (0, 1) for label in labels.values()):
        raise ValueError("Patch labels must be binary")
    negative = sorted(key for key, label in labels.items() if label == 0)
    positive = sorted(key for key, label in labels.items() if label == 1)
    if len(negative) < bag_size or len(positive) < positive_patches:
        raise ValueError("The split needs enough distinct patches for each bag")
    random = Random(seed)
    bags = []
    for label in (0, 1):
        for _ in range(count_per_class):
            positives = random.sample(positive, positive_patches) if label else []
            members = positives + random.sample(negative, bag_size - len(positives))
            random.shuffle(members)
            bags.append({"patches": members, "label": label, "positive_count": len(positives)})
    random.shuffle(bags)
    return bags


if __name__ == "__main__":
    for split, seed in (("train", 11), ("test", 23)):
        labels = {f"{split}-{index:02d}": int(index >= 6) for index in range(10)}
        bags = make_bags(labels, count_per_class=2, bag_size=4, positive_patches=1, seed=seed)
        print(split, bags)
