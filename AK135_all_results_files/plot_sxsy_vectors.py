#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def scale_color(nval):
    """
    Return an RGBA color based on NVAL.
    1 → pale red
    100 → dark red
    >100 → black
    """
    if nval > 100:
        return (0, 0, 0, 1)   # black

    # Scale 1..100 into 0.1..1.0 opacity
    alpha = 0.1 + 0.9 * (nval - 1) / 99.0
    return (1, 0, 0, alpha)  # red with variable opacity


def process_file(fname):

    station = fname.replace("_binned_sxsy.txt", "")
    print(f"Processing {station}")

    # Read columns
    theo_sx = []
    theo_sy = []
    meas_sx = []
    meas_sy = []
    nvals   = []

    with open(fname, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 5:
                continue

            tsx = float(parts[0])
            tsy = float(parts[1])
            msx = float(parts[2])
            msy = float(parts[3])
            n   = int(parts[4])

            dx = msx - tsx
            dy = msy - tsy
            length = np.hypot(dx, dy)

            # ✅ Skip vectors longer than 0.07
            if length > 0.07:
                continue

            theo_sx.append(tsx)
            theo_sy.append(tsy)
            meas_sx.append(msx)
            meas_sy.append(msy)
            nvals.append(n)

    if len(theo_sx) == 0:
        print(f" → No usable vectors for {station} (all >0.07).")
        return

    theo_sx = np.array(theo_sx)
    theo_sy = np.array(theo_sy)
    meas_sx = np.array(meas_sx)
    meas_sy = np.array(meas_sy)
    nvals   = np.array(nvals)

    dx = meas_sx - theo_sx
    dy = meas_sy - theo_sy

    # Create figure
    plt.figure(figsize=(8, 8))
    plt.title(f"{station}", fontsize=16)
    plt.xlabel("sx (s/km)")
    plt.ylabel("sy (s/km)")
    plt.grid(True, ls=":", color="0.8")

    # Build color list
    colors = [ scale_color(n) for n in nvals ]

    plt.quiver(
        theo_sx, theo_sy,
        dx, dy,
        angles='xy',
        scale_units='xy',
        scale=1.0,
        color=colors,
        width=0.004
    )

    # Axis limits
    xmin = min(theo_sx.min(), meas_sx.min()) - 0.02
    xmax = max(theo_sx.max(), meas_sx.max()) + 0.02
    ymin = min(theo_sy.min(), meas_sy.min()) - 0.02
    ymax = max(theo_sy.max(), meas_sy.max()) + 0.02
    #  plt.xlim(xmin, xmax)
    #  plt.ylim(ymin, ymax)
    plt.xlim(-0.35, 0.35)
    plt.ylim(-0.35, 0.35)


    # Save
    pngname = f"{station}_sxsy_vectors.png"
    pdfname = f"{station}_sxsy_vectors.pdf"
    plt.savefig(pngname, dpi=300)
    plt.savefig(pdfname)
    plt.close()

    print(f" → wrote {pngname}, {pdfname}")


def main():
    files = glob.glob("*_binned_sxsy.txt")
    if not files:
        print("No *_binned_sxsy.txt files found.")
        return

    for f in files:
        process_file(f)

if __name__ == "__main__":
    main()
