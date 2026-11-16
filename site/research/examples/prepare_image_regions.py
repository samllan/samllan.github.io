"""Turn selected centres or a regular grid into named image regions.

Record the bounds in source-image pixels so each crop can be traced back.
For example, a 4-pixel crop at (0, 0) has bounds (0, 0, 4, 4).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    label: str
    bounds: tuple[int, int, int, int]


def crop_from_clicks(image_size, size, centres):
    """Yield labelled squares around (x, y) centres, in click order."""
    width, height = image_size
    if not 0 < size <= min(width, height):
        raise ValueError("Crop size must fit inside the source image.")

    for number, (x, y) in enumerate(centres, start=1):
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"Centre {(x, y)} is outside the source image.")
        # Shift edge crops inward to keep every crop the same size.
        left = min(max(x - size // 2, 0), width - size)
        top = min(max(y - size // 2, 0), height - size)
        yield Region(f"crop-{number:02d}", (left, top, left + size, top + size))


def grid_patches(image_size, size, stride):
    """Yield complete patches in reading order, named by their origin."""
    width, height = image_size
    if not 0 < stride <= size <= min(width, height):
        raise ValueError("Use a positive stride no greater than the patch size.")

    for top in range(0, height - size + 1, stride):
        for left in range(0, width - size + 1, stride):
            yield Region(f"patch-x{left}-y{top}", (left, top, left + size, top + size))


def extract_regions(image, regions):
    """Pair each region record with pixels from an image supporting crop()."""
    for region in regions:
        yield region, image.crop(region.bounds)


if __name__ == "__main__":
    image_size = (12, 8)
    clicks = [(0, 0), (10, 6)]

    for region in crop_from_clicks(image_size, size=4, centres=clicks):
        print(region.label, region.bounds)

    patches = list(grid_patches(image_size, size=4, stride=4))
    print(f"{len(patches)} complete patches, ending at {patches[-1].bounds}")
