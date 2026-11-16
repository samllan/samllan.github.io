"""Check which held-out patches are most altered by reconstruction."""
import numpy as np


def reconstruction_errors(example_ids, original, decoded):
    original, decoded = np.asarray(original, dtype=float), np.asarray(decoded, dtype=float)
    if original.shape != decoded.shape or original.ndim != 2:
        raise ValueError("Pass matching sample-by-pixel arrays")
    if len(example_ids) != len(original) or len(set(example_ids)) != len(original):
        raise ValueError("Each sample needs a distinct ID")
    errors = np.mean((original - decoded) ** 2, axis=1)
    return sorted(zip(example_ids, errors.tolist()), key=lambda item: -item[1])


if __name__ == "__main__":
    print(reconstruction_errors(["a", "b"], [[0.0, 1.0], [0.2, 0.4]], [[0.1, 0.9], [0.4, 0.4]]))
