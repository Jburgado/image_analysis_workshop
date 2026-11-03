"""Smooth Nucleus_cropped_noise.tif with averaging (convolution) kernels.

Run it from the top folder of the workshop repository with:

    uv run src/mean_filter_nucleus.py

Each output pixel becomes a weighted average of its neighbors: every neighbor
is multiplied by the kernel weight at that position, and the products are
added up.  Each kernel is divided by the sum of its weights ("normalized"), so
the weights add up to 1 and the image keeps the same overall brightness.

Three kernels are tried:

    3x3 ones           3x3, center 4        7x7 ones
    1 1 1              1 1 1                (49 ones)
    1 1 1   / 9        1 4 1   / 12            / 49
    1 1 1              1 1 1

The results are saved next to the input, in testImages/:

    Nucleus_cropped_noise_mean_3x3.tif
    Nucleus_cropped_noise_mean_3x3_center4.tif
    Nucleus_cropped_noise_mean_7x7.tif

plus a side-by-side comparison picture Pictures/mean_filter_nucleus.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw into files only, no window on screen
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from scipy import ndimage

REPO = Path(__file__).resolve().parent.parent
INPUT = REPO / "testImages" / "Nucleus_cropped_noise.tif"
PICTURE = REPO / "Pictures" / "mean_filter_nucleus.png"

# The kernels, before normalizing.  Try changing the weights and run again.
center4 = np.ones((3, 3))
center4[1, 1] = 4  # the middle pixel counts 4 times as much as each neighbor
KERNELS = {
    "3x3": np.ones((3, 3)),
    "3x3_center4": center4,
    "7x7": np.ones((7, 7)),
}

# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray()
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
print(f"Read {INPUT.name}: {image.shape} pixels, type {image.dtype}")

results = {}
for name, kernel in KERNELS.items():
    # Normalize: divide every weight by the sum of all weights.
    kernel = kernel / kernel.sum()

    # Calculate with decimal numbers (float) so nothing gets rounded too early.
    # mode="nearest": at the border, missing neighbors are copies of the edge.
    filtered = ndimage.convolve(image.astype(float), kernel, mode="nearest")

    # Round back to whole numbers of the same type as the input (uint16).
    filtered = np.round(filtered).astype(image.dtype)
    results[name] = filtered

    # Save with the same pixel size and unit as the input image.
    output = INPUT.with_name(f"{INPUT.stem}_mean_{name}.tif")
    tifffile.imwrite(output, filtered, imagej=True, resolution=resolution,
                     metadata={"unit": unit})
    print(f"  {name:12s} kernel (weights sum to {kernel.sum():.2f}) -> saved {output.name}")
    print("   normalized kernel:\n", np.round(kernel, 3))

# Side-by-side picture: whole image on top, a zoomed-in part below.
panels = {"original (noisy)": image, **{f"mean {k}": v for k, v in results.items()}}
zoom = (slice(100, 160), slice(100, 160))  # a 60 x 60 pixel region to zoom into
vmin, vmax = np.percentile(image, [1, 99.5])
fig, axes = plt.subplots(2, len(panels), figsize=(4 * len(panels), 8))
for col, (title, img) in enumerate(panels.items()):
    axes[0, col].imshow(img, cmap="gray", vmin=vmin, vmax=vmax)
    axes[0, col].set_title(title, fontsize=13)
    axes[1, col].imshow(img[zoom], cmap="gray", vmin=vmin, vmax=vmax)
    axes[1, col].set_title("zoomed in", fontsize=11)
    for ax in axes[:, col]:
        ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
