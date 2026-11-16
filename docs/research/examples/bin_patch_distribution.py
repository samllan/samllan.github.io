"""Build a histogram table from recorded patch counts."""
from bisect import bisect_right


def histogram(counts, lower_bounds):
    bounds = list(lower_bounds)
    if not bounds or bounds[0] != 0 or any(a >= b for a, b in zip(bounds, bounds[1:])):
        raise ValueError("Bin lower bounds must start at zero and increase")
    bins = [0] * len(bounds)
    for count in counts:
        if count < 0:
            raise ValueError("Counts must be nonnegative")
        bins[bisect_right(bounds, count) - 1] += 1
    upper_bounds = [*bounds[1:], None]
    return list(zip(bounds, upper_bounds, bins))


if __name__ == "__main__":
    print("lower_inclusive,upper_exclusive,cores")
    for row in histogram([0, 20, 42, 79, 115, 128, 209], [0, 50, 100, 200]):
        print(*row, sep=",")
