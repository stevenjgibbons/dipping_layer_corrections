#!/usr/bin/env python3
import sys
import numpy as np

from transmit_slowness_snell_3D import (
    normal_from_strike_dip,
    incident_from_transmitted_snell_3d,
)

# ------------------------------------------------------------
# Usage
# ------------------------------------------------------------

def usage():
    print("Usage:\n")
    print(" python observed_to_theoretical.py "
          "vapp_predicted backazi_predicted alpha1 alpha2 strike dip\n")
    print("Example:")
    print(" python observed_to_theoretical.py 8.4 92.0 1.25 1.20 45 20\n")
    print(" python observed_to_theoretical.py 9.1 310.0 1.25 1.25 30 40\n")
    print(" python observed_to_theoretical.py 22.3  335.2  1.39  1.85  25  15   \n")
    sys.exit(1)


# ------------------------------------------------------------
# Convert apparent velocity + backazimuth → horizontal slowness
# ------------------------------------------------------------

def theoretical_slowness_from_vapp(vapp, backaz_deg):
    """
    Convert apparent velocity + backazimuth to horizontal slowness.

    backazimuth: clockwise from North (0=N, 90=E)
    Returns sx, sy in s/km
    """
    baz = np.deg2rad(backaz_deg)

    inv_vapp = 1.0 / vapp
    sx = inv_vapp * np.sin(baz)   # East
    sy = inv_vapp * np.cos(baz)   # North

    return sx, sy


# ------------------------------------------------------------
# Convert slowness vector → apparent velocity + backazimuth
# ------------------------------------------------------------

def vapp_bazi_from_slowness(sx, sy):
    """
    Convert horizontal slowness to apparent velocity and backazimuth
    (clockwise from North).
    """
    p = np.sqrt(sx**2 + sy**2)
    vapp = np.inf if p == 0.0 else 1.0 / p

    baz = np.rad2deg(np.arctan2(sx, sy)) % 360.0
    return vapp, baz


# ------------------------------------------------------------
# Recover theoretical slowness from observed slowness
# ------------------------------------------------------------

def recover_slowness(
    sx_obs, sy_obs,
    v_local_ak135,
    alpha1, alpha2,
    strike, dip
):
    """
    Invert Snell propagation: observed (below) -> theoretical (above).
    """

    # Plane normal
    nx, ny, nz = normal_from_strike_dip(strike, dip)

    # Vertical slowness below interface (down-going wave)
    inv_v2 = 1.0 / alpha2
    arg = inv_v2**2 - sx_obs**2 - sy_obs**2
    if arg < 0.0:
        raise ValueError("Evanescent wave: slowness below interface")

    sz_obs = -np.sqrt(arg)

    # Invert Snell's law
    sx_theo, sy_theo, sz_theo = incident_from_transmitted_snell_3d(
        sx_obs, sy_obs, sz_obs,
        nx=nx, ny=ny, nz=nz,
        v_above=alpha1,
        v_below=alpha2
    )

    return sx_theo, sy_theo


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    if len(sys.argv) != 7:
        usage()

    vapp_pred = float(sys.argv[1])
    backazi_pred = float(sys.argv[2])
    alpha1 = float(sys.argv[3])
    alpha2 = float(sys.argv[4])
    strike = float(sys.argv[5])
    dip = float(sys.argv[6])

    # Convert observed vapp/backazimuth → horizontal slowness
    sx_obs, sy_obs = theoretical_slowness_from_vapp(
        vapp_pred, backazi_pred
    )

    # Invert Snell transmission
    sx_theo, sy_theo = recover_slowness(
        sx_obs, sy_obs,
        v_local_ak135=None,
        alpha1=alpha1,
        alpha2=alpha2,
        strike=strike,
        dip=dip
    )

    # Convert back to apparent velocity + backazimuth
    vapp_theo, backazi_theo = vapp_bazi_from_slowness(
        sx_theo, sy_theo
    )

    print(f"vapp_theo = {vapp_theo:.6f} km/s")
    print(f"backazi_theo = {backazi_theo:.3f} deg")


if __name__ == "__main__":
    main()
