"""Apply a fixed resize and RGB normalisation before feature extraction."""
import numpy as np
from PIL import Image


def encoder_input(image, size, mean, standard_deviation):
    mean = np.asarray(mean, dtype=np.float32)
    scale = np.asarray(standard_deviation, dtype=np.float32)
    if mean.shape != (3,) or scale.shape != (3,) or not (scale > 0).all():
        raise ValueError("Supply one mean and positive scale per RGB channel")
    resized = image.convert("RGB").resize(size, Image.Resampling.BILINEAR)
    pixels = np.asarray(resized, dtype=np.float32) / 255
    return np.moveaxis((pixels - mean) / scale, -1, 0)


if __name__ == "__main__":
    patch = Image.new("RGB", (16, 20), "#95bbaf")
    channels = encoder_input(patch, (8, 8), [0.5] * 3, [0.25] * 3)
    print(channels.shape, channels[:, 0, 0].round(3))
