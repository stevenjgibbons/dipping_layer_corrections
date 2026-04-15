#!/usr/bin/env python3
import numpy as np
import glob
import os

def main():

    # Define grid
    sx_vals = np.linspace(-0.4, 0.4, 201)
    sy_vals = np.linspace(-0.4, 0.4, 201)

    # 2D arrays for storing lists of points
    bins_theo_sx = [[[] for _ in range(201)] for _ in range(201)]
    bins_theo_sy = [[[] for _ in range(201)] for _ in range(201)]
    bins_meas_sx = [[[] for _ in range(201)] for _ in range(201)]
    bins_meas_sy = [[[] for _ in range(201)] for _ in range(201)]

    files = glob.glob("*_all_arrivals_with_AK135sxsy.txt")

    for fname in files:
        print(f"Processing {fname}")

        # Station name prefix
        station = fname.replace("_all_arrivals_with_AK135sxsy.txt", "")
        outfile = f"{station}_binned_sxsy.txt"

        # Reset bins for each station
        bins_theo_sx = [[[] for _ in range(201)] for _ in range(201)]
        bins_theo_sy = [[[] for _ in range(201)] for _ in range(201)]
        bins_meas_sx = [[[] for _ in range(201)] for _ in range(201)]
        bins_meas_sy = [[[] for _ in range(201)] for _ in range(201)]

        # Read file (22 columns)
        with open(fname, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 22:
                    continue

                sx_theo = float(parts[20])  # col 21
                sy_theo = float(parts[21])  # col 22
                sx_meas = float(parts[17])  # col 18
                sy_meas = float(parts[18])  # col 19

                # Find nearest grid point in sx and sy
                ix = int(np.argmin(np.abs(sx_vals - sx_theo)))
                iy = int(np.argmin(np.abs(sy_vals - sy_theo)))

                # Store values
                bins_theo_sx[iy][ix].append(sx_theo)
                bins_theo_sy[iy][ix].append(sy_theo)
                bins_meas_sx[iy][ix].append(sx_meas)
                bins_meas_sy[iy][ix].append(sy_meas)

        # Write output
        with open(outfile, "w") as out:

            for iy in range(201):
                for ix in range(201):

                    N = len(bins_theo_sx[iy][ix])
                    if N == 0:
                        continue

                    med_tsx = float(np.median(bins_theo_sx[iy][ix]))
                    med_tsy = float(np.median(bins_theo_sy[iy][ix]))
                    med_msx = float(np.median(bins_meas_sx[iy][ix]))
                    med_msy = float(np.median(bins_meas_sy[iy][ix]))

                    out.write(f"{med_tsx:10.5f} {med_tsy:10.5f} "
                              f"{med_msx:10.5f} {med_msy:10.5f} {N:6d}\n")

        print(f" → Wrote {outfile}")

if __name__ == "__main__":
    main()
