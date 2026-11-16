"""Extract crops and keep their original pixel coordinates with the files."""
import argparse
import csv
from pathlib import Path

from PIL import Image

from prepare_image_regions import Region, crop_from_clicks


def extract_crops(image, image_id, regions, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for number, region in enumerate(regions, start=1):
        left, top, right, bottom = region.bounds
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ValueError(f"Invalid bounds for {region.label}")
        filename = f"crop-{number:03d}.png"
        image.crop(region.bounds).save(output_dir / filename)
        rows.append((image_id, region.label, filename, *region.bounds))
    manifest = output_dir / "crops.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("image", "label", "file", "left", "top", "right", "bottom"))
        writer.writerows(rows)
    return manifest


if __name__ == "__main__":
    from tempfile import TemporaryDirectory

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    image = Image.new("RGB", (32, 24), "#b57594")
    regions = [
        Region("rectangle", (2, 3, 12, 13)),
        *crop_from_clicks(image.size, 8, [(25, 12)]),
    ]
    if args.output:
        print(extract_crops(image, "demo-scan", regions, args.output).read_text())
    else:
        with TemporaryDirectory() as directory:
            print(extract_crops(image, "demo-scan", regions, Path(directory)).read_text())
