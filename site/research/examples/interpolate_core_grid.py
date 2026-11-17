"""Project a tilted microarray grid from two corner reference clicks.

In the August 2020 grid workflow, two corner clicks established the slide tilt
and average spacing across rows and columns. That cut marking time to 0.5
seconds per sample with 1.00 recall, while cores that drifted off the ideal
grid line reduced precision to 0.98.
"""
import math


def project_tilted_grid(first_corner, last_corner, *, rows, columns):
    """Estimate grid spacing and tilt from two reference centres in column 0."""
    if rows < 2 or columns < 1:
        raise ValueError("Need at least two rows and one column.")
    x1, y1 = first_corner
    x2, y2 = last_corner
    dx, dy = x2 - x1, y2 - y1
    if dy == 0:
        raise ValueError("Vertical span between reference corners must be nonzero.")

    theta = math.atan(dx / dy)
    spacing = math.hypot(dx, dy) / (rows - 1)
    half = spacing / 2
    for col_index in range(columns):
        col_label = chr(ord("A") + col_index)
        for row_index in range(rows):
            centre_x = x1 + col_index * spacing * math.cos(theta) + row_index * spacing * math.sin(theta)
            centre_y = y1 - col_index * spacing * math.sin(theta) + row_index * spacing * math.cos(theta)
            bounds = (
                round(centre_x - half), round(centre_y - half),
                round(centre_x + half), round(centre_y + half),
            )
            yield f"{row_index + 1}{col_label}", (round(centre_x), round(centre_y)), bounds


def centre_offset(projected_centre, observed_centre):
    """Measure how far an observed tissue core sits from its projected grid slot."""
    return round(math.hypot(observed_centre[0] - projected_centre[0], observed_centre[1] - projected_centre[1]), 1)


if __name__ == "__main__":
    observed = {"1A": (20, 20), "2A": (23, 50), "3A": (26, 80), "2B": (58, 44)}
    for label, centre, bounds in project_tilted_grid((20, 20), (26, 80), rows=3, columns=2):
        if label in observed:
            drift = centre_offset(centre, observed[label])
            print(f"{label}: projected {centre}, observed {observed[label]}, drift {drift} px, box {bounds}")
