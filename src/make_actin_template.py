"""Cut a small piece (a "template") out of Actin_Cropped.tif for cross-correlation.

Run it from the top folder of the workshop repository with:

    uv run src/make_actin_template.py

The result is saved as testImages/Actin_template.tif.
"""

from pathlib import Path

import tifffile

REPO = Path(__file__).resolve().parent.parent
INPUT = REPO / "testImages" / "Actin_Cropped.tif"
OUTPUT = REPO / "testImages" / "Actin_template.tif"

# The center of the piece (row, column) and how far it extends on each side.
# This spot lies on the bright stress fiber that runs diagonally through the
# top right part of the cell.  A half-width of 10 gives a 21 x 21 pixel piece.
CENTER_ROW, CENTER_COL = 50, 190
HALF_WIDTH = 10

with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray()
    # Keep the pixel size, so the template has the same size in microns.
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = tif.imagej_metadata.get("unit", "micron")

# "start:stop" picks rows (or columns) start up to, but not including, stop.
top, left = CENTER_ROW - HALF_WIDTH, CENTER_COL - HALF_WIDTH
template = image[top:CENTER_ROW + HALF_WIDTH + 1, left:CENTER_COL + HALF_WIDTH + 1]

tifffile.imwrite(OUTPUT, template, imagej=True, resolution=resolution,
                 metadata={"unit": unit})

print(f"Cut rows {top} - {top + template.shape[0] - 1}, "
      f"columns {left} - {left + template.shape[1] - 1} "
      f"({template.shape[0]} x {template.shape[1]} pixels)")
print(f"Saved {OUTPUT}")
