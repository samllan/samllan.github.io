"""Save selected patch pixels together with the selection manifest."""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from filter_tissue_patches import patch_selection


def save_patches(image, mask, core, folder, size, coverage):
    if image.size != mask.size:
        raise ValueError("Image and tissue mask must share coordinates")
    folder.mkdir(parents=True, exist_ok=True)
    manifest = folder / "patches.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("core", "file", "left", "top", "right", "bottom", "tissue_fraction"))
        for patch, fraction, keep in patch_selection(mask, size, size, coverage):
            if keep:
                name = f"{patch.label}.png"
                image.crop(patch.bounds).save(folder / name)
                writer.writerow((core, name, *patch.bounds, fraction))
    return manifest


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        image = Image.new("RGB", (16, 16), "#bd7896")
        mask = Image.new("1", image.size)
        mask.paste(1, (0, 0, 12, 8))
        print(save_patches(image, mask, "core-1", Path(directory), 8, 0.5).read_text())
