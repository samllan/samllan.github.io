"""Use a binary tissue mask to select grid patches for later processing."""
from PIL import Image

from prepare_image_regions import grid_patches


def patch_selection(mask, size, stride, minimum_coverage):
    if not 0 <= minimum_coverage <= 1:
        raise ValueError("Coverage must be between zero and one")
    binary = mask.convert("1", dither=Image.Dither.NONE)
    for patch in grid_patches(mask.size, size, stride):
        foreground = binary.crop(patch.bounds).histogram()[255]
        fraction = foreground / (size * size)
        yield patch, fraction, fraction >= minimum_coverage


if __name__ == "__main__":
    mask = Image.new("1", (16, 8))
    mask.paste(1, (0, 0, 9, 8))
    for patch, coverage, selected in patch_selection(mask, 4, 4, 0.5):
        print(patch.label, f"{coverage:.0%}", "keep" if selected else "skip")
