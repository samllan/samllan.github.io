"""Join supplied subtype labels to images without inferring missing labels."""


def match_labels(image_rows, reference, allowed=("ABC", "GCB")):
    kept, review = [], []
    seen = set()
    for image_id, reference_id in image_rows:
        if image_id in seen:
            raise ValueError(f"Duplicate image: {image_id}")
        seen.add(image_id)
        subtype = reference.get(reference_id)
        if subtype in allowed:
            kept.append((image_id, reference_id, subtype))
        else:
            review.append((image_id, reference_id, "missing" if subtype is None else "unrecognised"))
    return kept, review


if __name__ == "__main__":
    images = [("a", "R1"), ("b", "R2"), ("c", "R3")]
    print(match_labels(images, {"R1": "ABC", "R2": "unclassified"}))
