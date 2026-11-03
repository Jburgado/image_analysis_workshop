"""Sharpen Actin_cropped.tif by adding a fraction of the unsharp mask back.

First make the unsharp masks (only needed once):

    uv run src/gaussian_unsharp_actin.py

Then run this script from the top folder of the workshop repository with:

    uv run src/add_unsharp_mask_actin.py

The unsharp mask (input - blurred) holds only the fine details.  Adding some
of it back on top of the original makes those details stand out:

    result = input + FRACTION x mask

FRACTION = 0 gives the original image back; larger fractions sharpen more
(and also boost the noise more).

Saved in testImages/  (N = mask size, F = fraction):
    Actin_cropped_plus_F_mask_N.tif
and a comparison picture Pictures/add_unsharp_mask_actin.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw into files only, no window on screen
import matplotlib.pyplot as plt
import numpy as np
import tifffile

REPO = Path(__file__).resolve().parent.parent
FOLDER = REPO / "testImages"
INPUT = FOLDER / "Actin_cropped.tif"
PICTURE = REPO / "Pictures" / "add_unsharp_mask_actin.png"

MASK_SIZES = ["5x5", "21x21"]       # the masks made by gaussian_unsharp_actin.py
FRACTIONS = [0.25, 0.5, 1.0, 2.0]   # how much of the mask to add; try others

# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray()
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
print(f"Read {INPUT.name}: {image.shape} pixels, type {image.dtype}")

limits = np.iinfo(image.dtype)
results = {}  # (mask size, fraction) -> image
for size in MASK_SIZES:
    mask_file = FOLDER / f"{INPUT.stem}_unsharpmask_{size}.tif"
    if not mask_file.exists():
        raise SystemExit(f"{mask_file.name} not found - run "
                         "'uv run src/gaussian_unsharp_actin.py' first.")
    mask = tifffile.imread(mask_file)  # decimal numbers, can be negative
    print(f"  Read {mask_file.name}")

    for fraction in FRACTIONS:
        result = image.astype(float) + fraction * mask
        # Clip to the range a uint16 pixel can hold, then back to whole numbers.
        n_clipped = np.sum((result < limits.min) | (result > limits.max))
        result = np.clip(np.round(result), limits.min, limits.max).astype(image.dtype)
        results[(size, fraction)] = result

        # Save with the same pixel size and unit as the input image.
        output = FOLDER / f"{INPUT.stem}_plus_{fraction}_mask_{size}.tif"
        tifffile.imwrite(output, result, imagej=True, resolution=resolution,
                         metadata={"unit": unit})
        print(f"    + {fraction} x mask -> saved {output.name}"
              f"  ({n_clipped} pixels clipped)")

# Picture: one row per mask size, original first, then increasing fractions.
zoom = (slice(60, 180), slice(60, 180))  # 120 x 120 pixel region to zoom into
vmin, vmax = np.percentile(image, [1, 99.5])
ncols = len(FRACTIONS) + 1
fig, axes = plt.subplots(len(MASK_SIZES), ncols,
                         figsize=(3.6 * ncols, 4 * len(MASK_SIZES)))
for i, size in enumerate(MASK_SIZES):
    axes[i, 0].imshow(image[zoom], cmap="gray", vmin=vmin, vmax=vmax)
    axes[i, 0].set_title("original", fontsize=12)
    for j, fraction in enumerate(FRACTIONS, start=1):
        axes[i, j].imshow(results[(size, fraction)][zoom], cmap="gray",
                          vmin=vmin, vmax=vmax)
        axes[i, j].set_title(f"+ {fraction} x mask {size}", fontsize=12)
    for ax in axes[i]:
        ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
