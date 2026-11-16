"""Compare lossless PNG and a chosen WebP quality on the same RGB pixels."""

import argparse
from io import BytesIO
from pathlib import Path
from statistics import mean

from PIL import Image, ImageChops, ImageStat


def encode(image, format_name, **options):
    stream = BytesIO()
    image.save(stream, format=format_name, **options)
    return stream


def compare(path, quality):
    with Image.open(path) as source:
        pixels = source.convert('RGB')
    png = encode(pixels, 'PNG')
    webp = encode(pixels, 'WEBP', quality=quality)
    png_size, webp_size = png.tell(), webp.tell()
    webp.seek(0)
    with Image.open(webp) as decoded:
        error = mean(ImageStat.Stat(ImageChops.difference(pixels, decoded.convert('RGB'))).mean)
    return png_size, webp_size, error


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--quality', type=int, choices=range(101), metavar='0-100', default=75)
    args = parser.parse_args()
    png, webp, error = compare(args.image, args.quality)
    print(f'PNG: {png:,} bytes | WebP: {webp:,} bytes | Change: {(webp / png - 1):+.1%}')
    print(f'Mean absolute channel difference (0-255): {error:.2f}')
