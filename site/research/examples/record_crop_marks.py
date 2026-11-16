"""Save annotations as a CSV before extracting any image pixels.

The coordinate convention is left/top inclusive and right/bottom exclusive.
"""
import csv
import sys


def write_marks(output, image_id, image_size, marks):
    width, height = image_size
    rows = []
    seen = set()
    for label, kind, coordinates in marks:
        if label in seen:
            raise ValueError(f"Duplicate region label: {label}")
        seen.add(label)
        if kind == "point":
            x, y = coordinates
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Point outside image: {label}")
            bounds = (x, y, "", "")
        elif kind == "rectangle":
            left, top, right, bottom = coordinates
            if not (0 <= left < right <= width and 0 <= top < bottom <= height):
                raise ValueError(f"Rectangle outside image: {label}")
            bounds = coordinates
        else:
            raise ValueError(f"Unknown annotation type: {kind}")
        rows.append((image_id, label, kind, *bounds))

    writer = csv.writer(output)
    writer.writerow(("image", "label", "kind", "x", "y", "right", "bottom"))
    writer.writerows(rows)


if __name__ == "__main__":
    marks = [("A", "point", (20, 16)), ("B", "rectangle", (64, 44, 88, 68))]
    write_marks(sys.stdout, "demo-scan", (96, 72), marks)
