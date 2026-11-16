"""Trace a box on a downsampled crop back to source scan pixels."""


def to_scan_bounds(crop_origin, local_bounds, downsample):
    if downsample <= 0:
        raise ValueError("Downsample must be positive")
    left, top, right, bottom = local_bounds
    if not (0 <= left < right and 0 <= top < bottom):
        raise ValueError("Invalid local box")
    x, y = crop_origin
    return (
        x + left * downsample, y + top * downsample,
        x + right * downsample, y + bottom * downsample,
    )


if __name__ == "__main__":
    print(to_scan_bounds((1200, 800), (10, 8, 30, 28), downsample=4))
