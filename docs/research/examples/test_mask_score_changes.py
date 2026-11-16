"""Compare spatial dimming with a uniform control at the same mean brightness."""
import numpy as np


def compare_mask(model, image, mask):
    image = np.asarray(image, dtype=float)
    mask = np.asarray(mask, dtype=float)
    if image.shape != mask.shape or not mask.size or not ((mask >= 0) & (mask <= 1)).all():
        raise ValueError("Match the mask to the image and use brightness between zero and one")
    baseline = np.asarray(model(image))
    masked = np.asarray(model(image * mask))
    control = np.asarray(model(image * mask.mean()))
    return {"baseline": baseline, "spatial_delta": masked - baseline, "uniform_delta": control - baseline}


if __name__ == "__main__":
    def score(image):
        weights = np.array([[0.8, 0.1], [0.1, 0.0]])
        return [float((image * weights).sum())]

    print(compare_mask(score, [[0.9, 0.5], [0.5, 0.2]], [[0.2, 1], [1, 1]]))
