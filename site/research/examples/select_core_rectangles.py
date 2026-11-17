"""Scale hand-drawn bounding boxes from a zoomed preview to scan coordinates.

In the August 2020 annotation workflow, drawing a separate rectangle around each
core reached 1.00 precision and recall at 6 seconds per sample, while leaving
each extracted core with slightly different pixel dimensions.
"""
from typing import NamedTuple


class CoreBox(NamedTuple):
    label: str
    bounds: tuple[int, int, int, int]
    size: tuple[int, int]


def scale_drawn_rectangles(drawn_boxes, *, zoom_multiplier, display_scale):
    """Convert preview (left, top, width, height) boxes to full-scan bounds."""
    if zoom_multiplier <= 0 or display_scale <= 0:
        raise ValueError("Zoom multiplier and display scale must be positive.")

    factor = zoom_multiplier / display_scale
    for label, (left, top, width, height) in drawn_boxes:
        if min(width, height) <= 0 or min(left, top) < 0:
            raise ValueError(f"Invalid rectangle for {label}.")
        scan_left = round(left * factor)
        scan_top = round(top * factor)
        scan_width = round(width * factor)
        scan_height = round(height * factor)
        bounds = (scan_left, scan_top, scan_left + scan_width, scan_top + scan_height)
        yield CoreBox(label, bounds, (scan_width, scan_height))


if __name__ == "__main__":
    preview_boxes = [("1A", (18, 22, 122, 128)), ("1B", (164, 20, 129, 123))]
    for box in scale_drawn_rectangles(preview_boxes, zoom_multiplier=50, display_scale=1.25):
        print(f"{box.label}: bounds {box.bounds}, size {box.size[0]}x{box.size[1]} px")
