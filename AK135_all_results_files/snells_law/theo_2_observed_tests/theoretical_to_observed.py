#!/usr/bin/env python3
import sys
import numpy as np

from transmit_slowness_snell_3D import (
    normal_from_strike_dip,
    transmit_slowness_snell_3d,
    incident_from_transmitted_snell_3d,
)

def usage():
    print("Usage:\n")
    print("  python theoretical_to_observed.py  vapp_theo  backazi_theo  alpha1  alpha2  strike  dip\n")
    print("Example:")
    print("  python theoretical_to_observed.py  10.0  90.0  1.25  1.20  45  20\n")
    print("  python theoretical_to_observed.py  10.0 315.0  1.25  1.25  30  40\n")
    sys.exit(1)


# ------------------------------------------------------------
# Convert apparent velocity + backazimuth → horizontal slowness
# ------------------------------------------------------------
def theoretical_slowness_from_vapp(vapp, backaz_deg):
    """
    vapp: apparent velocity in km/s
    backaz_deg: backazimuth, clockwise from North (0=N, 90=E)

    Returns (sx, sy)
    with our ENU convention: x=East, y=North.
    """

    p = 1.0 / vapp
    baz = np.deg2rad(backaz_deg)

    # By seismological convention:
    # backaz 0° = from North, so pointing SOUTH in map view,
    # but our slowness (sx,sy) points BACK TO SOURCE.
    #
    # Therefore: sx = p * sin(baz),  sy = p * cos(baz)
    sx = p * np.sin(baz)
    sy = p * np.cos(baz)

    return sx, sy


# ------------------------------------------------------------
# Convert slowness vector → apparent velocity + backazimuth
# ------------------------------------------------------------
def vapp_bazi_from_slowness(sx, sy):
    """
    Returns (vapp, backazimuth_deg)
    backazimuth defined clockwise from North.
    """

    p_h = np.sqrt(sx*sx + sy*sy)
    if p_h == 0:
        return np.inf, 0.0

    vapp = 1.0 / p_h

    # Backazimuth = direction slowness vector points (back to source)
    # in ENU coordinates:
    # atan2(East, North) with clockwise-from-North conversion
    baz_rad = np.arctan2(sx, sy)   # atan2(East, North)
    baz_deg = np.degrees(baz_rad)
    if baz_deg < 0:
        baz_deg += 360.0

    return vapp, baz_deg


# ------------------------------------------------------------
# Perform Snell propagation (same as in your main model)
# ------------------------------------------------------------
def predict_slowness(sx_theor, sy_theor, v_local_ak135, alpha1, alpha2, strike, dip):

    # Build sz (downwards)
    inv_v = 1.0 / v_local_ak135
    horiz2 = sx_theor**2 + sy_theor**2
    if horiz2 >= inv_v**2:
        raise ValueError("Horizontal slowness too large for AK135 velocity.")
    sz_theor = -np.sqrt(inv_v**2 - horiz2)

    # Down through flat boundary
    v_below = alpha1 * v_local_ak135
    sx_d, sy_d, sz_d = transmit_slowness_snell_3d(
        sx_theor, sy_theor, sz_theor,
        nx=0, ny=0, nz=1,
        v_above=v_local_ak135,
        v_below=v_below
    )

    # Up through dipping boundary
    nx_d, ny_d, nz_d = normal_from_strike_dip(strike, dip)
    v_above_new = v_below / alpha2

    sx_p, sy_p, sz_p = incident_from_transmitted_snell_3d(
        sx_d, sy_d, sz_d,
        nx=nx_d, ny=ny_d, nz=nz_d,
        v_above=v_above_new,
        v_below=v_below
    )

    return sx_p, sy_p


# ------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------
def main():

    if len(sys.argv) != 7:
        usage()

    vapp_theo     = float(sys.argv[1])
    backazi_theo  = float(sys.argv[2])
    alpha1        = float(sys.argv[3])
    alpha2        = float(sys.argv[4])
    strike        = float(sys.argv[5])
    dip           = float(sys.argv[6])

    # Determine velocity (P or S) from apparent velocity
    # Logic: if vapp > ~4.5 km/s => assume P wave
    v_local_ak135 = 5.80 if vapp_theo > 4.5 else 3.46

    # Convert theoretical vapp and backazimuth into slowness
    sx_theo, sy_theo = theoretical_slowness_from_vapp(vapp_theo, backazi_theo)

    # Predict slowness after two Snell transitions
    try:
        sx_pred, sy_pred = predict_slowness(
            sx_theo, sy_theo,
            v_local_ak135,
            alpha1, alpha2,
            strike, dip
        )
    except Exception as e:
        print("Error in Snell propagation:", e)
        sys.exit(2)

    # Convert predicted slowness back to vapp & backazimuth
    vapp_pred, bazi_pred = vapp_bazi_from_slowness(sx_pred, sy_pred)

    print("\nINPUT")
    print("------")
    print(f"  vapp_theoretical    = {vapp_theo:.4f} km/s")
    print(f"  backazi_theoretical = {backazi_theo:.3f}°")
    print(f"  alpha1 = {alpha1},  alpha2 = {alpha2}")
    print(f"  strike = {strike}°, dip = {dip}°")
    print(f"  Using AK135 velocity: {v_local_ak135:.2f} km/s\n")

    print("PREDICTED")
    print("----------")
    print(f"  vapp_predicted      = {vapp_pred:.4f} km/s")
    print(f"  backazi_predicted   = {bazi_pred:.3f}°\n")

if __name__ == "__main__":
    main()
