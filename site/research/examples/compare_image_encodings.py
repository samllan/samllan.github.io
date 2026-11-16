"""Compare storage size and pixel change for two encodings of the same image.

The example encodes a generated patch. Install Pillow with WebP support to run it.
"""

from io import BytesIO
from typing import NamedTuple

from PIL import Image, ImageChops, ImageStat


class EncodingResult(NamedTuple):
    format: str
    size_bytes: int
    mean_pixel_difference: float


def compare_encodings(image, *, webp_quality=75):
    if not 0 <= webp_quality <= 100:
        raise ValueError("WebP quality must be between 0 and 100.")
    reference = image.convert("RGB")
    results = []
    for format_name, settings in (("PNG", {}), ("WebP", {"quality": webp_quality})):
        buffer = BytesIO()
        reference.save(buffer, format=format_name, **settings)
        size_bytes = buffer.tell()
        buffer.seek(0)

        # Decode both encodings before measuring. File size alone tells us
        # nothing about how much the pixels changed.
        with Image.open(buffer) as encoded:
            difference = ImageChops.difference(reference, encoded.convert("RGB"))
            mean_difference = sum(ImageStat.Stat(difference).mean) / 3
        results.append(EncodingResult(format_name, size_bytes, mean_difference))
    return results


if __name__ == "__main__":
    size = 48
    patch = Image.new("RGB", (size, size))
    patch.putdata([(5 * x, 5 * y, 2 * (x + y)) for y in range(size) for x in range(size)])
    print(f"{'Format':<8}{'Bytes':>8}{'Mean channel difference':>26}")
    for result in compare_encodings(patch):
        print(f"{result.format:<8}{result.size_bytes:>8}{result.mean_pixel_difference:>26.2f}")
