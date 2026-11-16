"""Place a score layer over an image using a shared display range."""
from pathlib import Path

import numpy as np
from PIL import Image

from map_patch_scores import score_grid


def render_overlay(image, scores, low=0.0, high=1.0):
    scores = np.asarray(scores, dtype=float)
    if scores.shape != (image.height, image.width) or not low < high:
        raise ValueError("Scores must align to the image and the range must increase")
    valid = np.isfinite(scores)
    intensity = np.clip((np.where(valid, scores, low) - low) / (high - low), 0, 1)
    overlay = np.zeros(scores.shape + (4,), dtype=np.uint8)
    overlay[..., 0] = 255
    overlay[..., 1] = (225 * (1 - intensity)).astype(np.uint8)
    overlay[..., 3] = np.where(valid, 75 + 95 * intensity, 0).astype(np.uint8)
    return Image.alpha_composite(image.convert("RGBA"), Image.fromarray(overlay))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sample = Image.new("RGB", (64, 48), "#634b68")
    scores = score_grid(sample.size, [(8, 8, 36, 28, 0.3), (20, 18, 56, 40, 0.8)])
    image = render_overlay(sample, scores)
    if args.output:
        image.save(args.output)
    print("Rendered", image.size, image.mode)
