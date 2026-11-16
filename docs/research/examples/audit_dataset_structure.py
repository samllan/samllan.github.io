"""Compare a dataset manifest with the arrays found in storage."""


def audit(expected_shapes, observed_shapes):
    missing = sorted(expected_shapes.keys() - observed_shapes.keys())
    extra = sorted(observed_shapes.keys() - expected_shapes.keys())
    mismatched = {
        name: (expected_shapes[name], observed_shapes[name])
        for name in sorted(expected_shapes.keys() & observed_shapes.keys())
        if expected_shapes[name] != observed_shapes[name]
    }
    return {"missing": missing, "unexpected": extra, "wrong_shape": mismatched}


if __name__ == "__main__":
    expected = {"A": (10, 64), "B": (8, 64)}
    observed = {"A": (10, 32), "spillover": (1, 64)}
    print(audit(expected, observed))
