"""Find edges in Actin_cropped.tif with the Sobel x and Sobel y kernels.

Run it from the top folder of the workshop repository with:

    uv run src/sobel_actin.py

Sobel x                 Sobel y
  -1  0  1               -1 -2 -1
  -2  0  2                0  0  0
  -1  0  1                1  2  1

Sobel x subtracts the pixels on the LEFT from the pixels on the RIGHT, so it
gives a large value where brightness changes from left to right (vertical
edges).  Positive = getting brighter to the right, negative = getting darker.
Sobel y does the same from top to bottom (horizontal edges).
The weights add up to 0, so flat regions give 0.  (They cannot be normalized
by their sum, because you cannot divide by 0.)

Gradient magnitude = how strong the edge is, in any direction:

    magnitude = square root of (sobel_x squared + sobel_y squared)

This is Pythagoras: sobel_x and sobel_y are the two sides of a right
triangle, and the magnitude is the long side.  Set SQUARE_ROOT = False below
to save sobel_x squared + sobel_y squared without the square root.

Saved in testImages/ as decimal numbers (float32, because Sobel results can be
negative):
    Actin_cropped_sobel_x.tif
    Actin_cropped_sobel_y.tif
    Actin_cropped_sobel_magnitude.tif
and a comparison picture Pictures/sobel_actin.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw into files only, no window on screen
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from scipy import ndimage

REPO = Path(__file__).resolve().parent.parent
INPUT = REPO / "testImages" / "Actin_cropped.tif"
PICTURE = REPO / "Pictures" / "sobel_actin.png"

SQUARE_ROOT = True  # True: real gradient magnitude.  False: x^2 + y^2 only.

SOBEL_X = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]], dtype=float)
SOBEL_Y = SOBEL_X.T  # the same kernel turned on its side (rows <-> columns)

# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray().astype(float)
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
print(f"Read {INPUT.name}: {image.shape} pixels")

# ndimage.correlate places the kernel on the image exactly as drawn above and
# multiplies-and-adds, like the step-by-step pictures in convolution_demo.py.
# (ndimage.convolve would first flip the kernel, which swaps the + and - signs.)
# mode="nearest": at the border, missing neighbors are copies of the edge.
sobel_x = ndimage.correlate(image, SOBEL_X, mode="nearest")
sobel_y = ndimage.correlate(image, SOBEL_Y, mode="nearest")

magnitude = sobel_x**2 + sobel_y**2
if SQUARE_ROOT:
    magnitude = np.sqrt(magnitude)

# Save with the same pixel size and unit as the input image.
outputs = {"sobel_x": sobel_x, "sobel_y": sobel_y, "sobel_magnitude": magnitude}
for name, data in outputs.items():
    path = INPUT.with_name(f"{INPUT.stem}_{name}.tif")
    tifffile.imwrite(path, data.astype(np.float32), imagej=True,
                     resolution=resolution, metadata={"unit": unit})
    print(f"  {name:16s} values {data.min():9.1f} to {data.max():9.1f}"
          f"  -> saved {path.name}")

# Picture.  For Sobel x and y: gray = 0, white = positive, black = negative.
fig, axes = plt.subplots(1, 4, figsize=(18, 5))
s = np.percentile(np.abs(np.concatenate([sobel_x, sobel_y])), 99.5)
panels = [
    (image, "original", *np.percentile(image, [1, 99.5])),
    (sobel_x, "Sobel x (left-right changes)", -s, s),
    (sobel_y, "Sobel y (top-bottom changes)", -s, s),
    (magnitude, "gradient magnitude" + ("" if SQUARE_ROOT else " (no sqrt)"),
     0, np.percentile(magnitude, 99.5)),
]
for ax, (img, title, lo, hi) in zip(axes, panels):
    ax.imshow(img, cmap="gray", vmin=lo, vmax=hi)
    ax.set_title(title, fontsize=13)
    ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
