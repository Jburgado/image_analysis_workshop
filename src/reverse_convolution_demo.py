"""Try to get the input image back from the output of a convolution ("deconvolution").

Run it from the top folder of the workshop repository with:

    uv run src/reverse_convolution_demo.py

It uses the same IMAGE and KERNEL as src/convolution_demo_edited.py, so if you
change the weights there, this script follows along automatically.

The idea
--------
Every output pixel is a weighted sum of input pixels, for example

    out[1,1] = -1*in[0,1] - 1*in[1,0] + 4*in[1,1] - 1*in[1,2] - 1*in[2,1]

So the output values plus the kernel give us a set of equations, and the input
pixels are the unknowns.  Recreating the input means solving those equations.

The script tries this twice:
  Attempt 1: we know ONLY the 9 output values and the kernel.
  Attempt 2: we also know the 16 pixels on the border of the input image.

The result is saved as Pictures/convolution/reconstruction.png
"""

import matplotlib
import numpy as np

matplotlib.use("Agg")  # draw into files only, no window on screen
import matplotlib.pyplot as plt

# Re-use the image, kernel and output folder from the convolution demo.
from convolution_demo_edited import IMAGE, KERNEL, OUT_DIR, kernel_cells

N = IMAGE.shape[0]                                       # 5 (image is 5 x 5)
CENTERS = [(r, c) for r in range(1, N - 1) for c in range(1, N - 1)]  # inner pixels


def convolve(image):
    """Same calculation as the demo: one output value per inner pixel."""
    out = np.zeros(image.shape)
    for r, c in CENTERS:
        out[r, c] = sum(w * image[rr, cc] for rr, cc, w in kernel_cells(r, c))
    return out


def build_equations():
    """Write the convolution as a table of equations:  A @ pixels = outputs.

    Each ROW of A is one output pixel.  Each COLUMN of A is one input pixel
    (the 5 x 5 image flattened into a list of 25 numbers).  The entry is the
    kernel weight with which that input pixel contributes to that output pixel.
    """
    A = np.zeros((len(CENTERS), N * N))
    for eq, (r, c) in enumerate(CENTERS):
        for rr, cc, w in kernel_cells(r, c):
            A[eq, rr * N + cc] = w
    return A


def main():
    output = convolve(IMAGE)
    y = np.array([output[r, c] for r, c in CENTERS])  # the 9 known output values
    A = build_equations()

    print("Original input image:\n", IMAGE)
    print("\nOutput values (inner 3 x 3):\n", output[1:-1, 1:-1].astype(int))

    # ---- Attempt 1: only the output and the kernel are known ---------------
    # 9 equations, 25 unknowns.  lstsq returns the "smallest" image that fits.
    print(f"\nAttempt 1: {A.shape[0]} equations but {A.shape[1]} unknown pixels.")
    guess1 = np.linalg.lstsq(A, y, rcond=None)[0].reshape(N, N)
    print("Recreated image:\n", np.round(guess1, 2))
    print("Does it give the same output again?",
          np.allclose(convolve(guess1), output))
    print("Is it the original image?          ", np.allclose(guess1, IMAGE))

    # ---- Attempt 2: we also know the border pixels -------------------------
    border = np.ones((N, N), dtype=bool)
    border[1:-1, 1:-1] = False              # True on the 16 border pixels
    b = border.ravel()
    # Move the known border pixels to the right-hand side of the equations,
    # leaving 9 equations for the 9 unknown inner pixels.
    y_inner = y - A[:, b] @ IMAGE.ravel()[b]
    inner = np.linalg.solve(A[:, ~b], y_inner)
    guess2 = IMAGE.astype(float).copy()
    guess2[1:-1, 1:-1] = inner.reshape(N - 2, N - 2)
    print(f"\nAttempt 2: border known -> {A[:, ~b].shape[0]} equations, "
          f"{A[:, ~b].shape[1]} unknowns.")
    print("Recreated image:\n", np.round(guess2, 2))
    print("Is it the original image?          ", np.allclose(guess2, IMAGE))

    # ---- Attempt 3: ASSUME each border pixel is a copy of its nearest -------
    # ---- inner pixel ("replicate the edge").  Only 9 unknowns are left. -----
    # P is a "copy table": P @ inner_pixels gives the full 5 x 5 image, where
    # each border pixel takes the value of the closest inner pixel.
    P = np.zeros((N * N, (N - 2) ** 2))
    for r in range(N):
        for c in range(N):
            rr = min(max(r, 1), N - 2) - 1   # nearest inner row (0..2)
            cc = min(max(c, 1), N - 2) - 1   # nearest inner column (0..2)
            P[r * N + c, rr * (N - 2) + cc] = 1
    A3 = A @ P                               # 9 equations, 9 unknowns
    rank = np.linalg.matrix_rank(A3)
    print(f"\nAttempt 3: assume border = copy of edge -> {A3.shape[0]} equations, "
          f"{A3.shape[1]} unknowns, but only {rank} of the equations are independent.")
    inner3 = np.linalg.lstsq(A3, y, rcond=None)[0]
    guess3 = (P @ inner3).reshape(N, N)
    print("Recreated image:\n", np.round(guess3, 2))
    print("Does it give the same output again?",
          np.allclose(convolve(guess3), output))
    print("Is it the original image?          ", np.allclose(guess3, IMAGE))
    print("Difference (recreated - original), inner pixels:\n",
          np.round(guess3 - IMAGE, 2)[1:-1, 1:-1])

    # ---- Picture -----------------------------------------------------------
    panels = [
        (IMAGE, "Original input"),
        (output[1:-1, 1:-1], "Output (inner 3x3)"),
        (guess1, "Attempt 1: output + kernel only"),
        (guess2, "Attempt 2: + known border"),
        (guess3, "Attempt 3: border = copied edge"),
    ]
    fig, axes = plt.subplots(1, 5, figsize=(20, 4.4))
    for ax, (img, title) in zip(axes, panels):
        ax.imshow(img, cmap="viridis")
        for (r, c), v in np.ndenumerate(img):
            ax.text(c, r, f"{v:.1f}", ha="center", va="center",
                    color="white", fontsize=10)
        ax.set_title(title, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "reconstruction.png", dpi=100)
    print(f"\nSaved picture to {OUT_DIR / 'reconstruction.png'}")


if __name__ == "__main__":
    main()
