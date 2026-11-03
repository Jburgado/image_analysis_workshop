"""Sharpen Actin_cropped.tif with a 3x3 sharpening kernel.

Run it from the top folder of the workshop repository with:

    uv run src/sharpen_actin.py

The kernel (before normalizing):

    -1  -1  -1
    -1  12  -1
    -1  -1  -1

How it sharpens: the center pixel is counted strongly (x12), and its 8
neighbors are subtracted (x -1).  In a flat region, where all pixels are about
the same, this changes little.  At an edge, where the center differs from its
neighbors, the difference is boosted, so edges and fine fibers stand out.

The weights add up to 12 - 8 = 4, so the kernel is divided by 4 ("normalized")
to keep the overall brightness of the image the same.

The result is saved as testImages/Actin_cropped_sharpened.tif, and a
side-by-side comparison picture as Pictures/sharpen_actin.png
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
OUTPUT = REPO / "testImages" / "Actin_cropped_sharpened.tif"
PICTURE = REPO / "Pictures" / "sharpen_actin.png"

# The sharpening kernel.  Try a different center weight (e.g. 9 or 16) and
# run again: a smaller center gives stronger sharpening.
KERNEL = np.array([[-1, -1, -1],
                   [-1, 12, -1],
                   [-1, -1, -1]], dtype=float)
KERNEL = KERNEL / KERNEL.sum()  # normalize, so the weights add up to 1

# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray()
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
print(f"Read {INPUT.name}: {image.shape} pixels, type {image.dtype}, "
      f"values {image.min()} - {image.max()}")
print("Normalized kernel:\n", KERNEL)

# Calculate with decimal numbers (float).
# mode="nearest": at the border, missing neighbors are copies of the edge.
sharpened = ndimage.convolve(image.astype(float), KERNEL, mode="nearest")

# Because of the negative weights, results can fall below 0 or above the
# largest value a uint16 pixel can hold (65535).  Such values are "clipped"
# to the allowed range before converting back to whole numbers.
limits = np.iinfo(image.dtype)
n_clipped = np.sum((sharpened < limits.min) | (sharpened > limits.max))
sharpened = np.clip(np.round(sharpened), limits.min, limits.max).astype(image.dtype)
print(f"Sharpened values {sharpened.min()} - {sharpened.max()} "
      f"({n_clipped} pixels had to be clipped)")

# Save with the same pixel size and unit as the input image.
tifffile.imwrite(OUTPUT, sharpened, imagej=True, resolution=resolution,
                 metadata={"unit": unit})
print(f"Saved {OUTPUT}")

# Side-by-side picture: whole image on top, a zoomed-in part below.
# Both images use the same gray scale, so they can be compared fairly.
panels = {"original": image, "sharpened": sharpened}
zoom = (slice(100, 160), slice(100, 160))  # a 60 x 60 pixel region to zoom into
vmin, vmax = np.percentile(image, [1, 99.5])
fig, axes = plt.subplots(2, len(panels), figsize=(5 * len(panels), 10))
for col, (title, img) in enumerate(panels.items()):
    axes[0, col].imshow(img, cmap="gray", vmin=vmin, vmax=vmax)
    axes[0, col].set_title(title, fontsize=14)
    axes[1, col].imshow(img[zoom], cmap="gray", vmin=vmin, vmax=vmax)
    axes[1, col].set_title("zoomed in", fontsize=12)
    for ax in axes[:, col]:
        ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
