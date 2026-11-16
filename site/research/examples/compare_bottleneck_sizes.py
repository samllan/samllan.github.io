"""Compare several bottlenecks on a common held-out set."""
import numpy as np

from fit_linear_autoencoder import decode, encode, fit_linear_autoencoder


def compare_bottlenecks(training, testing, widths):
    testing = np.asarray(testing)
    if testing.ndim != 2 or not len(testing):
        raise ValueError("Provide a nonempty test matrix")
    for width in widths:
        centre, basis = fit_linear_autoencoder(training, width)
        codes = encode(testing, centre, basis)
        mse = np.mean((testing - decode(codes, centre, basis)) ** 2)
        yield width, codes.nbytes, float(mse)


if __name__ == "__main__":
    training = [[0.2, 0.8, 0.4], [0.6, 0.3, 0.7], [0.5, 0.8, 0.1]]
    testing = [[0.3, 0.8, 0.2], [0.6, 0.4, 0.6]]
    print(list(compare_bottlenecks(training, testing, [1, 2])))
