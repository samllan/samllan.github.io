"""Calculate quadratic-weighted kappa on aligned ordinal grades."""
from collections import Counter


def weighted_kappa(pairs, levels):
    order = {grade: rank for rank, grade in enumerate(levels)}
    pairs = list(pairs)
    if not pairs or len(order) < 2 or len(order) != len(levels):
        raise ValueError("Provide paired grades and at least two distinct ordered levels")
    observed = Counter((order[a], order[b]) for a, b in pairs)
    first = Counter(order[a] for a, _ in pairs)
    second = Counter(order[b] for _, b in pairs)
    count = len(pairs)
    loss = sum((a - b) ** 2 * frequency for (a, b), frequency in observed.items()) / count
    expected = sum((a - b) ** 2 * n * m for a, n in first.items() for b, m in second.items()) / count**2
    if expected == 0:
        return None
    return 1 - loss / expected


if __name__ == "__main__":
    print(weighted_kappa([(0, 0), (1, 2), (2, 2), (3, 3)], [0, 1, 2, 3]))
