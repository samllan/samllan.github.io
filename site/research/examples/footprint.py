"""Calculate storage for fixed-length representations and compare against RGB pixels."""

import argparse


def footprint(items, height, width, features, feature_bytes=4):
    if min(items, height, width, features, feature_bytes) <= 0:
        raise ValueError('All dimensions and counts must be positive.')
    return items * height * width * 3, items * features * feature_bytes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--items', type=int, default=500)
    parser.add_argument('--height', type=int, default=224)
    parser.add_argument('--width', type=int, default=224)
    parser.add_argument('--features', type=int, default=256)
    parser.add_argument('--feature-bytes', type=int, default=4)
    args = parser.parse_args()
    image_bytes, vector_bytes = footprint(args.items, args.height, args.width, args.features, args.feature_bytes)
    print(f'Uncompressed RGB: {image_bytes:,} bytes')
    print(f'Feature vectors:  {vector_bytes:,} bytes')
    print(f'Footprint ratio:  {image_bytes / vector_bytes:.1f}x')
