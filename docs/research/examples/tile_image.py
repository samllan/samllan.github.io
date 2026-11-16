"""Split a regular image into full tiles and preserve each tile's source coordinates."""

import argparse
import csv
from pathlib import Path

from PIL import Image


def tile_bounds(width, height, size, stride):
    for top in range(0, height - size + 1, stride):
        for left in range(0, width - size + 1, stride):
            yield left, top, left + size, top + size


def extract_tiles(source, destination, size, stride):
    with Image.open(source) as image:
        if not 1 <= stride <= size <= min(image.size):
            raise ValueError('Choose a stride no greater than the tile size, and a tile that fits the image.')
        destination.mkdir(parents=True, exist_ok=True)
        with (destination / 'tile_manifest.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(('tile', 'left', 'top', 'right', 'bottom'))
            for box in tile_bounds(*image.size, size, stride):
                left, top, _, _ = box
                name = f'tile-x{left:04d}-y{top:04d}.png'
                image.crop(box).save(destination / name)
                writer.writerow((name, *box))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--size', type=int, default=96)
    parser.add_argument('--stride', type=int, default=64)
    args = parser.parse_args()
    extract_tiles(args.image, args.output, args.size, args.stride)
