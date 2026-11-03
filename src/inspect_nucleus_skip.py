"""Look inside an image, sampling every 3rd row and column of its numbers.

Same as inspect_nucleus.py, except the printed matrix skips 2 rows and 2
columns each time, so the 10 x 10 numbers are spread across a larger region.

Run it from the top folder of the workshop repository with:

    uv run src/inspect_nucleus_skip.py

That opens testImages/nucleus_cropped_1.tif.  To look at a different image,
put its path after the script name, for example:

    uv run src/inspect_nucleus_skip.py testImages/nucleus_cropped_2.tif

The numbers are printed in the terminal, then Napari opens in its own window.
Close that window to end the script.
"""

import argparse
from pathlib import Path

import napari
import numpy as np
import tifffile

# The image used when you do not name one.  Path(__file__) is this script,
# ".parent.parent" walks up two folders to the top of the workshop repository.
REPO = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = REPO / "testImages" / "nucleus_cropped_1.tif"

# Read the image path from the command line (the words typed after the script
# name).  If nothing was typed, use the default image.
parser = argparse.ArgumentParser(description="Show the numbers inside an image.")
parser.add_argument("image", nargs="?", default=DEFAULT_IMAGE, type=Path)
IMAGE = parser.parse_args().image

# Read the image.  To Python, an image is simply a grid (a "matrix") of
# numbers: one number per pixel, telling how bright that pixel is.
with tifffile.TiffFile(IMAGE) as tif:
    pixels = tif.asarray()
    # The file stores its resolution as "pixels per micrometer".  One divided
    # by that gives the size of one pixel in micrometers.  Not every file has
    # this information; then we fall back to 1 (sizes shown in pixels).
    resolution = tif.pages[0].tags.get("XResolution")
    if resolution is not None:
        numerator, denominator = resolution.value
        pixel_size = denominator / numerator
        unit = "um"
    else:
        pixel_size = 1.0
        unit = "pixel"

# 1. Ten rows and ten columns, skipping 2 rows and 2 columns each time.
#    Keeping one and skipping two means taking every 3rd one: a "step" of 3.
#    In Python "start:stop:step" picks numbers from start up to (not
#    including) stop, jumping by step.  "0:10*STEP:STEP" gives rows
#    0, 3, 6, ... 27 - ten of them.  Python counts from 0.
#    Widening the print line keeps each row of the matrix on one line.
STEP = 3
np.set_printoptions(linewidth=200)
print(f"Image: {IMAGE.name}")
print(f"10 rows and 10 columns, keeping 1 and skipping {STEP - 1} each time:")
print(f"  rows   : {list(range(0, 10 * STEP, STEP))}")
print(f"  columns: {list(range(0, 10 * STEP, STEP))}")
print(pixels[0 : 10 * STEP : STEP, 0 : 10 * STEP : STEP])
print()

# 2. The size of the image.  "shape" lists the length of each dimension;
#    for a 2D image that is (number of rows, number of columns).
rows, columns = pixels.shape
print(f"Number of rows   : {rows}")
print(f"Number of columns: {columns}")

# 3. The number type ("data type").  uint16 means "unsigned integer, 16 bits":
#    whole numbers, no negatives, from 0 up to 2**16 - 1 = 65535.
print(f"Number type      : {pixels.dtype}")
if np.issubdtype(pixels.dtype, np.integer):
    print(f"  smallest possible value: {np.iinfo(pixels.dtype).min}")
    print(f"  largest possible value : {np.iinfo(pixels.dtype).max}")
print(f"  values in this image   : {pixels.min()} - {pixels.max()}")
print(f"Pixel size       : {pixel_size:.3f} {unit}")

# 4. Show the image in Napari.  "scale" tells Napari how large each pixel is,
#    so the scale bar shows micrometers.
viewer = napari.Viewer()
viewer.add_image(
    pixels,
    name=IMAGE.stem,
    scale=(pixel_size, pixel_size),
    units=(unit, unit),
)
viewer.scale_bar.visible = True

# Start the Napari window and wait until you close it.
napari.run()
