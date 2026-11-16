"""Record which inclusion rule each sample passes or fails."""


def filter_cohort(records, *, required_stains, minimum_patches):
    accepted, excluded = [], {}
    known_ids = set()
    for sample, label, stains, patch_count in records:
        if sample in known_ids:
            raise ValueError(f"Duplicate sample: {sample}")
        known_ids.add(sample)
        reasons = []
        if label not in {"ABC", "GCB"}:
            reasons.append("target unavailable")
        if not required_stains.issubset(stains):
            reasons.append("required stain unavailable")
        if patch_count < minimum_patches:
            reasons.append("not enough retained patches")
        if reasons:
            excluded[sample] = reasons
        else:
            accepted.append(sample)
    return accepted, excluded


if __name__ == "__main__":
    examples = [("a", "ABC", {"stain-a"}, 12), ("b", None, set(), 4)]
    print(filter_cohort(examples, required_stains={"stain-a"}, minimum_patches=8))
