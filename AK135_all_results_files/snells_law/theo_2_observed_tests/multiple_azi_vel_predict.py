#!/usr/bin/env python3
"""
multiple_azi_vel_predict.py

Loop over theoretical backazimuth and predict observed apparent velocity
and backazimuth using the existing theoretical_to_observed machinery.

Usage
-----
python multiple_azi_vel_predict.py     alpha1 alpha2 strike dip azilo delazi azihi theo_appvel

Output
------
1) ASCII file: multiple_azi_vel_predict.out with columns
   theo_azi  theo_appvel  pred_azi  pred_appvel
2) PNG plot: multiple_azi_vel_predict.png
   x = theo_azi
   y = pred_azi - theo_azi
   points colored by pred_azi
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

from theoretical_to_observed import (
    theoretical_slowness_from_vapp,
    vapp_bazi_from_slowness,
    predict_slowness,
)

V_AK135 = 5.80  # km/s, consistent with theoretical_to_observed.py


def usage():
    print("Usage: ")
    print(" python multiple_azi_vel_predict.py alpha1 alpha2 strike dip azilo delazi azihi theo_appvel ")
    print("Example: ")
    print(" python multiple_azi_vel_predict.py 1.25 1.25 30 40 0 5 360 10.0 ") 
    sys.exit(1)


def main():
    if len(sys.argv) != 9:
        usage()

    alpha1 = float(sys.argv[1])
    alpha2 = float(sys.argv[2])
    strike = float(sys.argv[3])
    dip = float(sys.argv[4])
    azilo = float(sys.argv[5])
    delazi = float(sys.argv[6])
    azihi = float(sys.argv[7])
    theo_appvel = float(sys.argv[8])

    theo_azis = np.arange(azilo, azihi + 0.5 * delazi, delazi)

    rows = []

    for theo_azi in theo_azis:
        # Convert theoretical vapp + backazimuth to horizontal slowness
        sx_theo, sy_theo = theoretical_slowness_from_vapp(
            theo_appvel, theo_azi
        )

        # Predict transmitted slowness via Snell
        sx_pred, sy_pred = predict_slowness(
            sx_theo,
            sy_theo,
            V_AK135,
            alpha1,
            alpha2,
            strike,
            dip,
        )

        # Convert predicted slowness back to apparent velocity and backazimuth
        pred_appvel, pred_azi = vapp_bazi_from_slowness(sx_pred, sy_pred)

        rows.append((theo_azi, theo_appvel, pred_azi, pred_appvel))

    rows = np.array(rows)

    # Write ASCII output
    outname = "multiple_azi_vel_predict.out"
    header = "theo_azi  theo_appvel  pred_azi  pred_appvel"
    np.savetxt(outname, rows, fmt="%10.4f", header=header)

    # Plot
    theo_azi = rows[:, 0]
    pred_azi = rows[:, 2]
    pred_appvel = rows[:, 3]
    # delta_azi = pred_azi - theo_azi
    delta_azi = (pred_azi - theo_azi + 180.0) % 360.0 - 180.0

    plt.figure()
    sc = plt.scatter(theo_azi, delta_azi, c=pred_appvel, cmap="viridis")
    cb = plt.colorbar(sc)
    cb.set_label("Predicted apparent velocity (km/s)")
    plt.xlabel("Theoretical backazimuth (deg)")
    plt.ylabel("Predicted - Theoretical backazimuth (deg)")
    plt.ylim(-50.0, 50.0)
    plt.title("Backazimuth distortion vs theoretical azimuth")
    plt.grid(True)
    plt.savefig("multiple_azi_vel_predict.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Wrote {outname}")
    print(f"Wrote multiple_azi_vel_predict.png")


if __name__ == "__main__":
    main()
