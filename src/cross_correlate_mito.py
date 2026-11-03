"""Cross-correlate Mito_Cropped.tif with Mito_template.tif (no normalization).

Run it from the top folder of the workshop repository with:

    uv run src/cross_correlate_mito.py

Cross-correlation slides the small template over every position in the image.
At each position it multiplies the template pixels with the image pixels
underneath and adds everything up - exactly like applying a kernel, with the
template as the kernel.  The idea: where the image looks like the template,
the sum should be large.

No normalization is done: the raw sums are used as they are.

Saved:
    testImages/Mito_Cropped_xcorr.tif   the cross-correlation image (float32)
    Pictures/cross_correlate_mito.png   image + cross-correlation, with the
                                        highest value marked
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw into files only, no window on screen
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from scipy import ndimage

REPO = Path(__file__).resolve().parent.parent
IMAGE_FILE = REPO / "testImages" / "Mito_Cropped.tif"
TEMPLATE_FILE = REPO / "testImages" / "Mito_template.tif"
OUTPUT = REPO / "testImages" / "Mito_Cropped_xcorr.tif"
PICTURE = REPO / "Pictures" / "cross_correlate_mito.png"

# Where the template was cut out (center row, column), see make_mito_template.py.
# Only used to compare with the result.
TEMPLATE_CENTER = (225, 172)

# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(IMAGE_FILE) as tif:
    image = tif.asarray().astype(float)
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
template = tifffile.imread(TEMPLATE_FILE).astype(float)
pixel_size = resolution[0][1] / resolution[0][0]  # microns per pixel
print(f"Image:    {image.shape} pixels")
print(f"Template: {template.shape} pixels")

# Cross-correlation: correlate() puts the template (as is, not flipped) centered
# on every pixel, multiplies and adds.  mode="constant", cval=0 means that
# outside the image there is nothing (zeros).
xcorr = ndimage.correlate(image, template, mode="constant", cval=0.0)

# Find the highest value.  argmax gives its position in the flattened list,
# unravel_index turns that back into (row, column).
row, col = np.unravel_index(np.argmax(xcorr), xcorr.shape)
print(f"\nHighest value {xcorr[row, col]:.4g} at row {row}, column {col}"
      f"  (x = {col * pixel_size:.2f}, y = {row * pixel_size:.2f} {unit})")
tr, tc = TEMPLATE_CENTER
print(f"For comparison: value {xcorr[tr, tc]:.4g} at row {tr}, column {tc}"
      " - where the template was cut out")

# Save with the same pixel size and unit as the input image.
tifffile.imwrite(OUTPUT, xcorr.astype(np.float32), imagej=True,
                 resolution=resolution, metadata={"unit": unit})
print(f"\nSaved {OUTPUT}")

# Picture: image and cross-correlation, highest value marked with a red +,
# template origin with a cyan circle.
fig, axes = plt.subplots(1, 3, figsize=(15, 5.3),
                         gridspec_kw={"width_ratios": [1, 4, 4]})
axes[0].imshow(template, cmap="gray")
axes[0].set_title("template", fontsize=13)
axes[1].imshow(image, cmap="gray", vmin=np.percentile(image, 1),
               vmax=np.percentile(image, 99.5))
axes[1].set_title("Mito_Cropped", fontsize=13)
axes[2].imshow(xcorr, cmap="magma")
axes[2].set_title("cross-correlation (not normalized)", fontsize=13)
for ax in axes[1:]:
    ax.plot(col, row, "+", color="red", markersize=22, mew=3,
            label="highest value")
    ax.plot(tc, tr, "o", color="cyan", markersize=16, mfc="none", mew=2,
            label="template origin")
axes[2].legend(loc="lower right", fontsize=10)
for ax in axes:
    ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
