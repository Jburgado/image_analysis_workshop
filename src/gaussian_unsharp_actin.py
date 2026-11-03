"""Gaussian blur and unsharp masking of Actin_cropped.tif.

Run it from the top folder of the workshop repository with:

    uv run src/gaussian_unsharp_actin.py

1. Gaussian blur.  A Gaussian kernel is a weighted average where the center
   pixel counts most, and the weights fall off smoothly (bell-shaped) with
   distance.  Two kernel sizes are used: 5x5 (a little blur) and 21x21 (a lot).
   The width of the bell ("sigma") is chosen so that the kernel reaches 3 sigma
   from the center to the edge: sigma = (size - 1) / 6.

2. Unsharp mask = input - blurred.  The blurred image contains only the coarse
   structures, so subtracting it leaves the fine details (fibers, edges).
   The result has positive AND negative values, so it is saved as decimal
   numbers (float32) instead of whole numbers.

3. Sharpened = input + AMOUNT x unsharp mask.  Adding the details back on top
   of the original is the classic "unsharp masking" sharpening method (it is
   what the "Unsharp Mask" filter in ImageJ/Fiji and Photoshop does).

Saved in testImages/  (N = 5x5 or 21x21):
    Actin_cropped_gauss_N.tif        blurred
    Actin_cropped_unsharpmask_N.tif  input - blurred
    Actin_cropped_sharpened_N.tif    input + AMOUNT x (input - blurred)
and a comparison picture Pictures/gaussian_unsharp_actin.png
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
PICTURE = REPO / "Pictures" / "gaussian_unsharp_actin.png"

KERNEL_SIZES = [5, 21]  # try other odd numbers, e.g. 11
AMOUNT = 1.0            # how strongly the details are added back (try 0.5 or 2)


def gaussian_kernel(size):
    """Make a size x size Gaussian kernel whose weights add up to 1."""
    sigma = (size - 1) / 6
    x = np.arange(size) - size // 2          # e.g. -2 -1 0 1 2 for size 5
    bell = np.exp(-x**2 / (2 * sigma**2))    # 1D bell curve
    kernel = np.outer(bell, bell)            # 2D: rows x columns
    return kernel / kernel.sum(), sigma      # normalize


def save(path, data):
    """Save with the same pixel size and unit as the input image."""
    tifffile.imwrite(path, data, imagej=True, resolution=resolution,
                     metadata={"unit": unit})
    print(f"    saved {path.name}")


# Read the image and its pixel size (stored as "pixels per micron").
with tifffile.TiffFile(INPUT) as tif:
    image = tif.asarray()
    page = tif.pages[0]
    resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
    unit = (tif.imagej_metadata or {}).get("unit", "micron")
print(f"Read {INPUT.name}: {image.shape} pixels, type {image.dtype}")

limits = np.iinfo(image.dtype)
original = image.astype(float)
rows = []
for size in KERNEL_SIZES:
    kernel, sigma = gaussian_kernel(size)
    print(f"  {size}x{size} Gaussian kernel, sigma = {sigma:.2f} pixels")
    tag = f"{size}x{size}"

    # 1. Blur (mode="nearest": at the border, copy the edge pixels).
    blurred = ndimage.convolve(original, kernel, mode="nearest")
    save(INPUT.with_name(f"{INPUT.stem}_gauss_{tag}.tif"),
         np.round(blurred).astype(image.dtype))

    # 2. Unsharp mask: the fine details only.  Can be negative -> float32.
    mask = original - blurred
    save(INPUT.with_name(f"{INPUT.stem}_unsharpmask_{tag}.tif"),
         mask.astype(np.float32))

    # 3. Sharpened: details added back on top of the original.
    sharpened = np.clip(np.round(original + AMOUNT * mask), limits.min, limits.max)
    save(INPUT.with_name(f"{INPUT.stem}_sharpened_{tag}.tif"),
         sharpened.astype(image.dtype))

    rows.append((tag, blurred, mask, sharpened))

# Picture: one row per kernel size: original | blurred | mask | sharpened.
vmin, vmax = np.percentile(image, [1, 99.5])
fig, axes = plt.subplots(len(rows), 4, figsize=(16, 4.8 * len(rows)))
for i, (tag, blurred, mask, sharpened) in enumerate(rows):
    m = np.percentile(np.abs(mask), 99.5)  # symmetric scale around 0 for the mask
    panels = [
        (image, "original", "gray", vmin, vmax),
        (blurred, f"Gaussian {tag}", "gray", vmin, vmax),
        (mask, f"unsharp mask {tag}\n(input - blurred)", "gray", -m, m),
        (sharpened, f"sharpened {tag}\n(input + {AMOUNT} x mask)", "gray", vmin, vmax),
    ]
    for ax, (img, title, cmap, lo, hi) in zip(axes[i], panels):
        ax.imshow(img, cmap=cmap, vmin=lo, vmax=hi)
        ax.set_title(title, fontsize=12)
        ax.axis("off")
fig.tight_layout()
PICTURE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(PICTURE, dpi=100)
print(f"Saved comparison picture {PICTURE}")
