"""Print the Red, Green and Blue values of a regular grid of pixels.

Run it from the top folder of the workshop repository with:

    uv run src/rgb_pixel_table.py

That opens testImages/Cell_cropped_2.tif.  To look at a different RGB image,
put its path after the script name, for example:

    uv run src/rgb_pixel_table.py testImages/Cell_cropped_2.jpg

About 3% of the pixels, evenly spaced over the image, are listed in a table in
the terminal.  Then Napari opens with the image; the sampled pixels are marked
with small dots.  Close the Napari window to end the script.
"""

import argparse
from pathlib import Path

import napari
import numpy as np
from bioio import BioImage

REPO = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = REPO / "testImages" / "Cell_cropped_2.tif"
FRACTION = 0.03  # 3% of the pixels

parser = argparse.ArgumentParser(description="Table of RGB values of an image.")
parser.add_argument("image", nargs="?", default=DEFAULT_IMAGE, type=Path)
IMAGE = parser.parse_args().image

# BioImage stores the three colors of an RGB picture in the "S" (samples)
# dimension.  "YXS" asks for rows, columns, and then the 3 color values, so
# pixels[row, column] gives [R, G, B] for one pixel.
img = BioImage(IMAGE)
pixels = img.get_image_data("YXS")
n_rows, n_cols, n_colors = pixels.shape
if n_colors != 3:
    raise SystemExit(f"{IMAGE.name} has {n_colors} color values per pixel, not 3 (RGB).")

# Pick pixels on a regular grid: every "step"-th row and every "step"-th
# column.  Such a grid keeps 1 out of step * step pixels, so to keep 3% we
# need step * step = 1 / 0.03 = 33.3, i.e. step = about 6.
step = max(1, round(1 / np.sqrt(FRACTION)))
rows = np.arange(step // 2, n_rows, step)   # start half a step in, so the
cols = np.arange(step // 2, n_cols, step)   # grid sits nicely centered
n_sampled = len(rows) * len(cols)

print(f"Image: {IMAGE.name}  ({n_rows} rows x {n_cols} columns = {n_rows * n_cols} pixels)")
print(f"Number type: {pixels.dtype}  (values {pixels.min()} - {pixels.max()})")
print(f"Every {step}th row and column -> {n_sampled} pixels "
      f"({100 * n_sampled / (n_rows * n_cols):.1f}% of the image)")
print()

# The table: one line per sampled pixel.  ":>5" means "right-align in a
# space 5 characters wide", which keeps the columns lined up.
print(f"{'row':>5} {'col':>5} | {'R':>5} {'G':>5} {'B':>5}")
print("-" * 31)
for r in rows:
    for c in cols:
        red, green, blue = pixels[r, c]
        print(f"{r:>5} {c:>5} | {red:>5} {green:>5} {blue:>5}")

# Show the image in Napari.  rgb=True tells Napari the last dimension holds
# the three colors, so it shows one color picture instead of three layers.
# "scale" is the pixel size, so the scale bar shows micrometers when the
# file stores a pixel size.
sizes = img.physical_pixel_sizes
pixel_size = sizes.X if sizes.X else 1.0
unit = "um" if sizes.X else "pixel"

viewer = napari.Viewer()
viewer.add_image(pixels, name=IMAGE.stem, rgb=True,
                 scale=[pixel_size, pixel_size], units=[unit, unit])

# Mark the sampled pixels with small dots so you can see where the grid is.
# Hide this layer (eye icon in the layer list) to see the plain image.
grid_r, grid_c = np.meshgrid(rows, cols, indexing="ij")
viewer.add_points(np.column_stack([grid_r.ravel(), grid_c.ravel()]),
                  name="sampled pixels", size=1, face_color="white",
                  border_width=0, scale=[pixel_size, pixel_size], units=[unit, unit])
viewer.canvas.overlays.scale_bar.visible = True

napari.run()
