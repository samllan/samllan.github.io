"""Extract and name image regions from a table of centre clicks (requires Pillow)."""

import argparse
import csv
import re
from pathlib import Path

from PIL import Image


def crop_box(x, y, size, image_size):
    """Keep a fixed-size crop inside the image, including near an edge."""
    width, height = image_size
    if not 0 < size <= min(width, height):
        raise ValueError('Crop size must fit inside the image.')
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f'Click ({x}, {y}) lies outside the image.')
    left = min(max(x - size // 2, 0), width - size)
    top = min(max(y - size // 2, 0), height - size)
    return left, top, left + size, top + size


def extract_crops(image_path, clicks_path, output_path, size):
    with Image.open(image_path) as image, clicks_path.open(newline='', encoding='utf-8-sig') as stream:
        crops = {}
        for row in csv.DictReader(stream):
            label = row['label'].strip().lower()
            if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', label) or label in crops:
                raise ValueError(f'Invalid or repeated label: {label!r}')
            crops[label] = crop_box(int(row['x']), int(row['y']), size, image.size)

        output_path.mkdir(parents=True, exist_ok=True)
        with (output_path / 'crop_manifest.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(('label', 'file', 'left', 'top', 'right', 'bottom'))
            for label, box in crops.items():
                filename = f'crop-{label}.png'
                image.crop(box).save(output_path / filename)
                writer.writerow((label, filename, *box))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('clicks', type=Path, help='CSV with label, x and y columns, in image pixels')
    parser.add_argument('output', type=Path)
    parser.add_argument('--size', type=int, default=96)
    args = parser.parse_args()
    extract_crops(args.image, args.clicks, args.output, args.size)
