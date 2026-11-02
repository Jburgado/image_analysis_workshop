"""List all TIFF tags of an image file in a human-readable way.

Run it from the top folder of the workshop repository with:

    uv run src/show_tiff_tags.py

That reads testImages/Cell_cropped.tif.  To look at a different TIFF file,
put its path after the script name, for example:

    uv run src/show_tiff_tags.py testImages/Cell_cropped_2.tif

A TIFF file stores its pixels in one or more "pages" (often one per channel,
slice or time point).  Every page carries a list of "tags": numbered labels
with a value, such as the image width or the number of bits per pixel.
The first page is shown in full; for the other pages only the tags whose
value differs from the first page are shown.
"""

import argparse
from pathlib import Path

import numpy as np
import tifffile

REPO = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = REPO / "testImages" / "Cell_cropped.tif"

parser = argparse.ArgumentParser(description="Show the TIFF tags of an image.")
parser.add_argument("image", nargs="?", default=DEFAULT_IMAGE, type=Path)
IMAGE = parser.parse_args().image

# Plain-English meaning of the most common tags.  Tags not in this list are
# still shown, just without an explanation.
MEANING = {
    "NewSubfileType": "kind of page (0 = normal full-resolution image)",
    "ImageWidth": "number of columns (pixels from left to right)",
    "ImageLength": "number of rows (pixels from top to bottom)",
    "BitsPerSample": "bits per number (8 -> 0-255, 16 -> 0-65535)",
    "Compression": "how the pixel data is compressed (1 = not compressed)",
    "PhotometricInterpretation": "how to turn numbers into colors",
    "ImageDescription": "free text; programs store their own metadata here",
    "StripOffsets": "where in the file the pixel data starts (in bytes)",
    "SamplesPerPixel": "numbers per pixel (1 = grey, 3 = RGB)",
    "RowsPerStrip": "rows stored together in one block ('strip')",
    "StripByteCounts": "size of each block of pixel data (in bytes)",
    "XResolution": "pixels per unit length, left to right",
    "YResolution": "pixels per unit length, top to bottom",
    "PlanarConfiguration": "RGB stored as RGBRGB... (1) or RRR..GGG..BBB.. (2)",
    "ResolutionUnit": "unit for X/YResolution (1 = none, 2 = inch, 3 = cm)",
    "Software": "program that wrote the file",
    "DateTime": "date and time the file was written",
    "SampleFormat": "number type (1 = unsigned integer, 2 = signed, 3 = float)",
    "IJMetadataByteCounts": "ImageJ: sizes of the ImageJ metadata blocks",
    "IJMetadata": "ImageJ: extra metadata (display ranges, color tables, ...)",
}


def readable(value):
    """Turn a tag value into short, readable text (a list of lines)."""
    # Named constants such as <PHOTOMETRIC.MINISBLACK: 1>
    if hasattr(value, "name") and hasattr(value, "value"):
        return [f"{value.name} ({value.value})"]
    # Fractions, e.g. XResolution = (3088326, 1000000) = 3.088 pixels/unit
    if (isinstance(value, tuple) and len(value) == 2
            and all(isinstance(v, int) for v in value) and value[1] not in (0, 1)):
        return [f"{value[0]}/{value[1]} = {value[0] / value[1]:.6g}"]
    # Text with several lines: show each line on its own
    if isinstance(value, str):
        return value.strip().splitlines() or [""]
    # Big tables of numbers (e.g. color look-up tables): describe, don't print
    if isinstance(value, np.ndarray):
        return [f"table of {value.size} numbers, shape {value.shape}, {value.dtype}"]
    # Dictionaries (ImageJ metadata): one line per entry
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (list, tuple)) and item and isinstance(item[0], np.ndarray):
                item = f"{len(item)} tables of shape {item[0].shape}"
            lines.append(f"{key}: {item}")
        return lines
    text = str(value)
    return [text if len(text) <= 100 else text[:100] + " ..."]


def print_tag(tag):
    lines = readable(tag.value)
    print(f"{tag.code:>6}  {tag.name:<27} {lines[0]}")
    for line in lines[1:]:
        print(f"{'':>6}  {'':<27} {line}")
    if tag.name in MEANING:
        print(f"{'':>6}  {'':<27} -> {MEANING[tag.name]}")


with tifffile.TiffFile(IMAGE) as tif:
    pages = tif.pages
    print(f"File : {IMAGE.name}")
    print(f"Pages: {len(pages)}")
    if tif.is_imagej:
        print("Written by ImageJ/Fiji")
    print()

    print(f"=== Page 1 of {len(pages)} ===")
    print(f"{'code':>6}  {'tag name':<27} value")
    first = {tag.code: tag for tag in pages[0].tags}
    for tag in first.values():
        print_tag(tag)

    # The other pages usually repeat the same tags.  Only show the differences.
    for number, page in enumerate(pages[1:], start=2):
        print(f"\n=== Page {number} of {len(pages)}: tags that differ from page 1 ===")
        differ = False
        for tag in page.tags:
            same = (tag.code in first
                    and str(tag.value) == str(first[tag.code].value))
            if not same:
                print_tag(tag)
                differ = True
        if not differ:
            print("(none)")

    # The resolution tags hide the pixel size: pixel size = 1 / resolution.
    tags = pages[0].tags
    if "XResolution" in tags:
        num, den = tags["XResolution"].value
        if num:
            unit = "um" if tif.is_imagej and (tif.imagej_metadata or {}).get("unit") in ("micron", "um") else "unit"
            print(f"\nPixel size (1 / XResolution): {den / num:.4f} {unit}")
