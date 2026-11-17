"""Turn an instance segmentation into traceable cell crops.

A labelled mask contains one integer per cell and zero for background.
The demo labels separated shapes with simple thresholding. The research
used a trained instance segmenter to separate cells in tissue.
"""
from typing import NamedTuple

import numpy as np


class CellCrop(NamedTuple):
    instance: int
    scan_centre: tuple[float, float]
    pixels: np.ndarray


def label_foreground(foreground):
    """Label four-connected regions in a small synthetic binary image."""
    if foreground.ndim != 2:
        raise ValueError("Use a two-dimensional foreground mask")
    labels = np.zeros(foreground.shape, dtype=int)
    height, width = labels.shape
    identifier = 0
    for y, x in zip(*np.nonzero(foreground)):
        if labels[y, x]:
            continue
        identifier += 1
        labels[y, x] = identifier
        pending = [(y, x)]
        while pending:
            row, column = pending.pop()
            neighbours = ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1))
            for next_row, next_col in neighbours:
                if (0 <= next_row < height and 0 <= next_col < width
                        and foreground[next_row, next_col] and not labels[next_row, next_col]):
                    labels[next_row, next_col] = identifier
                    pending.append((next_row, next_col))
    return labels


def extract_cell_crops(image, labels, *, crop_size, min_width, max_width, scan_origin=(0, 0)):
    if labels.ndim != 2 or image.shape[:2] != labels.shape:
        raise ValueError("The image and instance mask need the same height and width")
    if crop_size < 1 or not 1 <= min_width <= max_width:
        raise ValueError("Use a positive crop size and an ordered width range")
    if not np.issubdtype(labels.dtype, np.integer) or np.any(labels < 0):
        raise ValueError("Mask labels must be nonnegative integers")

    height, width = labels.shape
    offset_x, offset_y = scan_origin
    for identifier in np.unique(labels):
        if identifier == 0:
            continue
        ys, xs = np.nonzero(labels == identifier)
        extent = 1 + max(xs.max() - xs.min(), ys.max() - ys.min())
        if not min_width <= extent <= max_width:
            continue
        x, y = float(xs.mean()), float(ys.mean())
        left, top = round(x) - crop_size // 2, round(y) - crop_size // 2
        right, bottom = left + crop_size, top + crop_size
        if left < 0 or top < 0 or right > width or bottom > height:
            continue
        yield CellCrop(int(identifier), (x + offset_x, y + offset_y), image[top:bottom, left:right].copy())


if __name__ == "__main__":
    y, x = np.mgrid[:24, :32]
    image = np.full((24, 32), 220, dtype=np.uint8)
    for cx, cy in ((9, 10), (22, 14)):
        image[(x - cx)**2 + (y - cy)**2 <= 4] = 125
    mask = label_foreground(image < 160)
    for crop in extract_cell_crops(image, mask, crop_size=8, min_width=3, max_width=7, scan_origin=(240, 520)):
        print(f"Cell {crop.instance}: scan centre {crop.scan_centre}, crop {crop.pixels.shape}")
