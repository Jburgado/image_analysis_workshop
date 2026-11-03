"""Find all mitochondria that look like Mito_template.tif, using normalized
cross-correlation (skimage match_template), and show them in napari.

Run it from the top folder of the workshop repository with:

    uv run src/match_template_mito.py

Normalized cross-correlation works like plain cross-correlation (slide the
template over the image, multiply and add), but at every position the template
and the image patch are first corrected for their own brightness and contrast.
The result is a number between -1 and 1:

     1  = the patch has exactly the same shape as the template
     0  = no similarity
    -1  = the exact opposite (bright where the template is dark)

So a bright region no longer wins just because it is bright.

Peaks: positions with a value above THRESHOLD that are at least MIN_DISTANCE
pixels apart (if two peaks are closer, only the higher one is kept).

Saved:  testImages/Mito_Cropped_ncc.tif   the normalized cross-correlation image
Napari opens with the image, the correlation image, and circles on the peaks.
"""

from pathlib import Path

import napari
import numpy as np
import tifffile
from skimage.feature import match_template, peak_local_max

REPO = Path(__file__).resolve().parent.parent
IMAGE_FILE = REPO / "testImages" / "Mito_Cropped.tif"
TEMPLATE_FILE = REPO / "testImages" / "Mito_template.tif"
OUTPUT = REPO / "testImages" / "Mito_Cropped_ncc.tif"

THRESHOLD = 0.8     # only peaks with a value above this count as a match
MIN_DISTANCE = 4    # peaks must be at least this many pixels apart


def find_matches():
    """Calculate the normalized cross-correlation and find its peaks."""
    with tifffile.TiffFile(IMAGE_FILE) as tif:
        image = tif.asarray()
        page = tif.pages[0]
        resolution = (page.tags["XResolution"].value, page.tags["YResolution"].value)
        unit = (tif.imagej_metadata or {}).get("unit", "micron")
    template = tifffile.imread(TEMPLATE_FILE)
    pixel_size = resolution[0][1] / resolution[0][0]  # microns per pixel

    # pad_input=True: the result has the same size as the image, and each value
    # belongs to the pixel at the CENTER of the template.  So a peak at
    # (row, column) means "a match centered on this pixel of the image".
    ncc = match_template(image.astype(float), template.astype(float),
                         pad_input=True)

    # peak_local_max finds local maxima: pixels higher than their surroundings.
    # It returns a list of (row, column) positions, highest peak first.
    peaks = peak_local_max(ncc, min_distance=MIN_DISTANCE, threshold_abs=THRESHOLD)

    # Save with the same pixel size and unit as the input image.
    tifffile.imwrite(OUTPUT, ncc.astype(np.float32), imagej=True,
                     resolution=resolution, metadata={"unit": unit})

    print(f"Normalized cross-correlation: values {ncc.min():.2f} to {ncc.max():.2f}")
    print(f"Found {len(peaks)} peaks above {THRESHOLD}, "
          f"at least {MIN_DISTANCE} pixels apart:")
    for row, col in peaks:
        print(f"  row {row:3d}, column {col:3d}   value {ncc[row, col]:.3f}")
    print(f"Saved {OUTPUT}")
    return image, template, ncc, peaks, pixel_size, unit


def show_in_napari(image, template, ncc, peaks, pixel_size, unit):
    """Show image, correlation and peaks in napari, at the real size in microns."""
    scale = (pixel_size, pixel_size)  # napari uses this to show microns
    viewer = napari.Viewer()
    viewer.add_image(ncc, name="normalized cross-correlation", scale=scale,
                     colormap="magma", contrast_limits=(-1, 1), visible=False)
    viewer.add_image(image, name="Mito_Cropped", scale=scale)
    # Points are given in pixels (row, column); "scale" turns them into microns,
    # so they land on the right spot.  size = circle diameter, here the
    # template width (11 pixels), drawn as rings.
    viewer.add_points(peaks, name=f"matches > {THRESHOLD}", scale=scale,
                      symbol="ring", size=template.shape[0],
                      face_color="yellow", border_width=0)
    viewer.scale_bar.visible = True
    viewer.scale_bar.unit = "um" if unit == "micron" else unit
    napari.run()


if __name__ == "__main__":
    show_in_napari(*find_matches())
