#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# ------------------------------------------------------------
# Color scaling for each velocity-dependent color scheme
# ------------------------------------------------------------

def shade(color_base, nval):
    """
    Darken a base RGB color according to nval (1–limitval).
    Returns an (r,g,b,1) tuple.
    """
    # clamp nval to [1, limitval]
    limitval = 400
    n = max(1, min(nval, limitval))

    # scale 1..100 → 0.2..1.0 intensity
    factor = 0.35 + 0.65 * (n - 1) / (limitval-1)

    r = color_base[0] * factor
    g = color_base[1] * factor
    b = color_base[2] * factor
    return (r, g, b, 1)


def color_from_velocity(vapp, nval):
    """
    Choose color scale by apparent velocity (vapp)
    and apply darkening via nval.
    """

    if vapp > 25.0:
        # brown scale (base light brown)
        return shade((0.66, 0.33, 0.0), nval)

    elif vapp > 10.0:
        # red scale
        return shade((1.0, 0.0, 0.0), nval)

    elif vapp > 5.9:
        # blue scale
        return shade((0.0, 0.3, 1.0), nval)

    else:
        # green scale
        return shade((0.0, 0.6, 0.0), nval)


# ------------------------------------------------------------
# Process each station file
# ------------------------------------------------------------
def process_file(fname):

    station = fname.replace("_binned_sxsy.txt", "")
    print(f"Processing {station}")

    theo_sx = []
    theo_sy = []
    meas_sx = []
    meas_sy = []
    nvals = []

    with open(fname, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 5:
                continue

            tsx = float(parts[0])
            tsy = float(parts[1])
            msx = float(parts[2])
            msy = float(parts[3])
            n = int(parts[4])

            dx = msx - tsx
            dy = msy - tsy

            # skip long vectors
            if np.hypot(dx, dy) > 0.10:
                continue

            theo_sx.append(tsx)
            theo_sy.append(tsy)
            meas_sx.append(msx)
            meas_sy.append(msy)
            nvals.append(n)

    if len(theo_sx) == 0:
        print(f" → No usable vectors for {station} (all > 0.10).")
        return

    theo_sx = np.array(theo_sx)
    theo_sy = np.array(theo_sy)
    meas_sx = np.array(meas_sx)
    meas_sy = np.array(meas_sy)
    nvals = np.array(nvals)

    dx = meas_sx - theo_sx
    dy = meas_sy - theo_sy

    # ------------------------------------------------------------
    # Compute apparent velocity for each vector tail
    # ------------------------------------------------------------
    vapp = 1.0 / np.sqrt(theo_sx**2 + theo_sy**2)

    # Build colors for each vector
    colors = [color_from_velocity(v, n)
              for v, n in zip(vapp, nvals)]

    # ------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------
    plt.figure(figsize=(8, 8))
    plt.title(f"{station}", fontsize=16)
    plt.xlabel("sx (s/km)")
    plt.ylabel("sy (s/km)")
    plt.grid(True, ls=":", color="0.8")

    plt.quiver(
        theo_sx, theo_sy,
        dx, dy,
        angles='xy',
        scale_units='xy',
        scale=1.0,
        color=colors,
        width=0.004
    )

    plt.xlim(-0.35, 0.35)
    plt.ylim(-0.35, 0.35)

    pngname = f"{station}_sxsy_vectors.png"
    pdfname = f"{station}_sxsy_vectors.pdf"
    plt.savefig(pngname, dpi=300)
    plt.savefig(pdfname)
    plt.close()
    print(f" → wrote {pngname}, {pdfname}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    files = glob.glob("*_binned_sxsy.txt")
    if not files:
        print("No *_binned_sxsy.txt files found.")
        return

    for f in files:
        process_file(f)


if __name__ == "__main__":
    main()
