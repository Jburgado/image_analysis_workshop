"""Look inside an image: its numbers, its size, its number type.

Run it from the top folder of the workshop repository with:

    uv run src/inspect_nucleus.py

That opens testImages/nucleus_cropped_1.tif.  To look at a different image,
put its path after the script name, for example:

    uv run src/inspect_nucleus.py testImages/nucleus_cropped_2.jpg

Any format BioImage can read works (TIFF, OME-TIFF, JPG, PNG, ND2, ICS, ...),
including images with several channels, z-slices or time points.

The numbers are printed in the terminal, then Napari opens in its own window.
Close that window to end the script.
"""

import argparse
from pathlib import Path

import napari
import numpy as np
from bioio import BioImage

# The image used when you do not name one.  Path(__file__) is this script,
# ".parent.parent" walks up two folders to the top of the workshop repository.
REPO = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = REPO / "testImages" / "nucleus_cropped_1.tif"

# Read the image path from the command line (the words typed after the script
# name).  If nothing was typed, use the default image.
parser = argparse.ArgumentParser(description="Show the numbers inside an image.")
parser.add_argument("image", nargs="?", default=DEFAULT_IMAGE, type=Path)
IMAGE = parser.parse_args().image

# BioImage opens many microscopy formats and reads the metadata stored with
# the pixels.  It describes every image with five dimensions:
#   T = time points, C = channels, Z = slices, Y = rows, X = columns.
# A plain 2D picture simply has T, C and Z all equal to 1.
img = BioImage(IMAGE)

# Keep only the dimensions that hold more than one value (plus Y and X, which
# every image has).  For a plain 2D image this leaves "YX"; for a 3-channel
# image "CYX", and so on.
dims = "".join(d for d in "TCZYX" if d in "YX" or getattr(img.dims, d) > 1)
pixels = img.get_image_data(dims)

# Some files store their numbers in "big-endian" byte order (most significant
# byte first).  Convert to the computer's own order; the values do not change.
pixels = pixels.astype(pixels.dtype.newbyteorder("="))

# How large one pixel is in the sample, in micrometers.  Not every file
# stores this; then we fall back to 1 (sizes shown in pixels).
sizes = img.physical_pixel_sizes
pixel_size = sizes.X if sizes.X else 1.0
unit = "um" if sizes.X else "pixel"
z_step = sizes.Z if sizes.Z else 1.0

# 1. The first 10 rows and 10 columns.  "plane[0:10, 0:10]" means: rows 0 up
#    to (not including) 10, and columns 0 up to 10.  Python counts from 0.
#    If the image has channels, slices or time points, we look at the very
#    first 2D picture: the last two dimensions are always rows and columns,
#    so we pick index 0 of every dimension in front of them.
#    Widening the print line keeps each row of the matrix on one line.
plane = pixels[(0,) * (pixels.ndim - 2)]
np.set_printoptions(linewidth=200)
print(f"Image: {IMAGE.name}")
if pixels.ndim > 2:
    print("(showing the first channel / slice / time point)")
print("First 10 rows and 10 columns of pixel values:")
print(plane[0:10, 0:10])
print()

# 2. The size of the image.  "shape" lists the length of each dimension.
names = {"T": "time points", "C": "channels", "Z": "slices",
         "Y": "rows", "X": "columns"}
for d, length in zip(dims, pixels.shape):
    print(f"Number of {names[d]:12s}: {length}")
if "C" in dims:
    print(f"Channel names         : {[str(c) for c in img.channel_names]}")

# 3. The number type ("data type").  uint16 means "unsigned integer, 16 bits":
#    whole numbers, no negatives, from 0 up to 2**16 - 1 = 65535.
print(f"Number type           : {pixels.dtype}")
if np.issubdtype(pixels.dtype, np.integer):
    print(f"  smallest possible value: {np.iinfo(pixels.dtype).min}")
    print(f"  largest possible value : {np.iinfo(pixels.dtype).max}")
print(f"  values in this image   : {pixels.min()} - {pixels.max()}")
print(f"Pixel size            : {pixel_size:.3f} {unit}")

# 4. Show the image in Napari.  "scale" tells Napari how large each pixel is
#    along every dimension, so the scale bar shows micrometers.  If there are
#    channels, "channel_axis" makes one layer per channel, and additive
#    blending overlays their colors like on a fluorescence microscope.
scale_of = {"T": 1.0, "Z": z_step, "Y": pixel_size, "X": pixel_size}
unit_of = {"T": "", "Z": unit, "Y": unit, "X": unit}
spatial = [d for d in dims if d != "C"]

viewer = napari.Viewer()
if "C" in dims:
    viewer.add_image(
        pixels,
        channel_axis=dims.index("C"),
        name=[str(c) for c in img.channel_names],
        blending="additive",
        scale=[scale_of[d] for d in spatial],
        units=[unit_of[d] for d in spatial],
    )
else:
    viewer.add_image(
        pixels,
        name=IMAGE.stem,
        scale=[scale_of[d] for d in spatial],
        units=[unit_of[d] for d in spatial],
    )
viewer.canvas.overlays.scale_bar.visible = True

# Start the Napari window and wait until you close it.
napari.run()
