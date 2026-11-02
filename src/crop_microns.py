"""Crop a square region, given in micrometers, out of a multi-channel image.

Run it from the top folder of the workshop repository with:

    uv run src/crop_microns.py

It opens
    testImages/3Channel_FF_Corrected_1/3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif
cuts out a 100 x 100 micrometer square centered on the position set below,
saves it as an OME-TIFF next to the original (pixel size included), and shows
the result in Napari.  Close the Napari window to end the script.

To crop somewhere else, change CENTER_X_UM / CENTER_Y_UM / SIZE_UM below.
"""

from pathlib import Path

import napari
from bioio import BioImage
from bioio_ome_tiff.writers import OmeTiffWriter

REPO = Path(__file__).resolve().parent.parent
IMAGE = (REPO / "testImages" / "3Channel_FF_Corrected_1"
         / "3Channel_FF_Corrected_1_MMStack_Pos0.ome.tif")

# ---- The crop, in micrometers -------------------------------------------
# Tip: Napari's status bar shows the cursor position as [y x] (y first!).
CENTER_X_UM = 186.243   # left-right position of the center
CENTER_Y_UM = 385.069    # top-bottom position of the center
SIZE_UM = 100.0         # width and height of the square
CHANNELS = ["Cy3", "FITC", "DAPI"]  # e.g. ["DAPI"] to keep only DAPI
# ---------------------------------------------------------------------------

img = BioImage(IMAGE)
pixel_size = img.physical_pixel_sizes.X   # micrometers per pixel
if not pixel_size:
    raise SystemExit("This image has no pixel size, so micrometers cannot be converted.")

# "CYX" = channels, rows (Y), columns (X).  The other dimensions (T and Z)
# have length 1 in this file, so we leave them out.
pixels = img.get_image_data("CYX")
n_rows, n_cols = pixels.shape[1:]

# Convert micrometers to pixels: divide by the size of one pixel.
# Pixels are whole numbers, so we round.
size_px = round(SIZE_UM / pixel_size)
x_start = round(CENTER_X_UM / pixel_size - size_px / 2)
y_start = round(CENTER_Y_UM / pixel_size - size_px / 2)

if x_start < 0 or y_start < 0 or x_start + size_px > n_cols or y_start + size_px > n_rows:
    raise SystemExit("The crop sticks out of the image; choose a center further inside.")

# The crop itself.  "a:b" means "from a up to (not including) b".
channel_names = [str(c) for c in img.channel_names]
keep = [channel_names.index(name) for name in CHANNELS]
cropped = pixels[keep, y_start:y_start + size_px, x_start:x_start + size_px]

print(f"Pixel size : {pixel_size} um")
print(f"Crop       : x {x_start} - {x_start + size_px - 1}, "
      f"y {y_start} - {y_start + size_px - 1} (pixels)")
print(f"Result     : {cropped.shape[0]} channels x {size_px} x {size_px} pixels "
      f"= {size_px * pixel_size:.2f} x {size_px * pixel_size:.2f} um, {cropped.dtype}")

# Save as OME-TIFF.  Passing physical_pixel_sizes copies the pixel size into
# the new file, so other programs still know how large a pixel is.
out_path = IMAGE.parent / f"crop_x{CENTER_X_UM:.0f}um_y{CENTER_Y_UM:.0f}um_{SIZE_UM:.0f}um.ome.tif"
OmeTiffWriter.save(
    cropped,
    out_path,
    dim_order="CYX",
    channel_names=CHANNELS,
    physical_pixel_sizes=img.physical_pixel_sizes,
)
print(f"Saved      : {out_path.relative_to(REPO)}")

# Show the saved file, read back from disk, so you check what was really
# written.  Each channel becomes its own layer with its own color.
saved = BioImage(out_path)
viewer = napari.Viewer()
viewer.add_image(
    saved.get_image_data("CYX"),
    channel_axis=0,
    name=[str(c) for c in saved.channel_names],
    colormap=["magenta", "green", "blue"][:len(CHANNELS)],
    blending="additive",
    scale=[saved.physical_pixel_sizes.Y, saved.physical_pixel_sizes.X],
    units=["um", "um"],
)
viewer.canvas.overlays.scale_bar.visible = True
napari.run()
