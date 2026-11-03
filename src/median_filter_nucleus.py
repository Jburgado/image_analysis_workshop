"""Remove the salt-and-pepper noise from Nucleus_cropped_noise.tif with median filters.

Run it from the top folder of the workshop repository with:

    uv run src/median_filter_nucleus.py

A median filter looks at each pixel together with its neighbors (the pixels
covered by the "kernel" or "footprint"), sorts those values, and replaces the
pixel with the middle value.  A single very bright or very dark noise pixel
ends up at one end of the sorted list, so it is thrown away.

Three kernels are tried (1 = pixel is used, 0 = pixel is ignored):

    plus (3x3, no corners)   square 3x3      square 5x5
        0 1 0                  1 1 1          1 1 1 1 1
        1 1 1                  1 1 1          1 1 1 1 1
        0 1 0                  1 1 1          1 1 1 1 1
                                              1 1 1 1 1
                                              1 1 1 1 1

The results are saved next to the input, in testImages/:

    Nucleus_cropped_noise_median_plus3x3.tif
    Nucleus_cropped_noise_median_3x3.tif
    Nucleus_cropped_noise_median_5x5.tif

plus a side-by-side comparison picture Pictures/median_filter_nucleus.png
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
PICTURE = REPO / "Pictures" / "median_filter_nucleus.png"

# The kernels.  Try changing them (for example a 7x7 square) and run again.
KERNELS = {
    "plus3x3": np.array([[0, 1, 0],
                         [1, 1, 1],
                         [0, 1, 0]], dtype=bool),
    "3x3": np.ones((3, 3), dtype=bool),
    "5x5": np.ones((5, 5), dtype=bool),
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
    # footprint = which neighbors take part.  mode="nearest" means that at the
    # image border, missing neighbors are filled with copies of the edge pixel.
    filtered = ndimage.median_filter(image, footprint=kernel, mode="nearest")
    results[name] = filtered

    # Save with the same pixel size and unit as the input image.
    output = INPUT.with_name(f"{INPUT.stem}_median_{name}.tif")
    tifffile.imwrite(output, filtered, imagej=True, resolution=resolution,
                     metadata={"unit": unit})
    print(f"  {name:8s} kernel ({kernel.sum():2d} pixels) -> saved {output.name}")

# Side-by-side picture: whole image on top, a zoomed-in corner below.
panels = {"original (noisy)": image, **{f"median {k}": v for k, v in results.items()}}
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
