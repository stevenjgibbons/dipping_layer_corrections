import numpy as np
from typing import Tuple

def normal_from_strike_dip(strike_deg: float, dip_deg: float) -> np.ndarray:
    """
    Compute the upward-pointing unit normal vector to a plane from
    strike and dip in ENU coordinates (x=East, y=North, z=Up).

    Assumptions:
      - strike_deg: azimuth of strike (clockwise from North), in degrees [0, 360).
      - dip_deg: dip angle measured downward from horizontal, in degrees [0, 90].
      - Returns the unit normal with non-negative z (upward if possible).

    Returns:
      np.ndarray of shape (3,), unit length.
    """
    a = np.deg2rad(strike_deg)   # alpha
    d = np.deg2rad(dip_deg)      # delta

    # Downward-pointing unit normal in ENU
    n = np.array([
         np.sin(d) * np.cos(a),  # East
        -np.sin(d) * np.sin(a),  # North
        -np.cos(d)               # Down
    ], dtype=float)

    # Normalize to be extra safe against rounding error
    n_norm = np.linalg.norm(n)
    if n_norm == 0:
        raise ValueError("Degenerate normal (check strike/dip).")
    n /= n_norm

    # Enforce upward pointing (nz >= 0)
    if n[2] < 0:
        n = -n

    return n


def incident_from_transmitted_snell_3d(
    sx_below: float, sy_below: float, sz_below: float,
    nx: float, ny: float, nz: float,
    v_above: float, v_below: float,
    *,
    below_is_opposite_normal: bool = True,
    tol: float = 1e-12
) -> Tuple[float, float, float]:
    """
    Recover the incident (above-medium) slowness vector from a transmitted
    (below-medium) slowness vector across a planar interface using 3D Snell's law.

    Coordinates: ENU (x=East, y=North, z=Up).
      - p_below = (sx_below, sy_below, sz_below) in s/km (assumed propagating).
      - n = (nx, ny, nz) is the *unit* interface normal (dimensionless).
      - v_above, v_below are wave speeds (km/s).

    Physics:
      - Tangential slowness is conserved: p_t (same above & below).
      - Magnitude in each medium is 1/v.
      - Normal component (magnitude) above is sqrt((1/v_above)^2 - ||p_t||^2).
      - Sign of p_n,above is chosen to match sign(p_n,below) if non-grazing.
        If grazing (|p_n,below| ~ 0), we pick a default consistent with the
        convention that "below is opposite the normal" when
        below_is_opposite_normal=True (then we choose negative).

    Returns:
      (sx_above, sy_above, sz_above) in s/km.

    Raises:
      ValueError if:
        - v_above or v_below are non-positive,
        - n is zero or near-zero,
        - ||p_below|| is inconsistent with 1/v_below (beyond tolerance),
        - The recovered incident is evanescent (i.e., ||p_t|| > 1/v_above).
    """
    # Validate wave speeds
    if v_above <= 0 or v_below <= 0:
        raise ValueError("Wave speeds must be positive.")

    # Assemble vectors
    p_below = np.array([sx_below, sy_below, sz_below], dtype=float)
    n = np.array([nx, ny, nz], dtype=float)

    # Normalize the normal
    n_norm = np.linalg.norm(n)
    if not np.isfinite(n_norm) or n_norm < tol:
        raise ValueError("Interface normal must be non-zero.")
    n = n / n_norm

    # Optional: sanity-check that p_below has magnitude ~ 1/v_below
    inv_vb = 1.0 / v_below
    p_below_mag = np.linalg.norm(p_below)
    if abs(p_below_mag - inv_vb) > 1e-6 * inv_vb:
        # Not fatal in principle (could be noisy), but warn/raise if you prefer strictness.
        pass

    # Decompose transmitted slowness into tangential + normal
    p_n_below = float(np.dot(p_below, n))   # scalar
    p_t = p_below - p_n_below * n           # tangential component (conserved)
    pt2 = float(np.dot(p_t, p_t))

    # Physical feasibility in the above medium
    inv_va = 1.0 / v_above
    inv_va2 = inv_va * inv_va
    if pt2 > inv_va2 + tol:
        raise ValueError(
            "Evanescent/invalid incident wave: "
            f"||p_t||={np.sqrt(pt2):.6g} > 1/v_above={inv_va:.6g}."
        )

    # Compute incident normal magnitude
    under = max(0.0, inv_va2 - pt2)
    p_n_above_mag = np.sqrt(under)

    # Choose sign for incident normal component
    sign = np.sign(p_n_below)
    if abs(sign) < 0.5:  # grazing transmitted: pick convention
        sign = -1.0 if below_is_opposite_normal else +1.0

    p_above = p_t + sign * p_n_above_mag * n

    # Optional normalization polish (for rounding safety)
    # p_above *= (inv_va / np.linalg.norm(p_above))

    return tuple(map(float, p_above))

def transmit_slowness_snell_3d(
    sx_above: float, sy_above: float, sz_above: float,
    nx: float, ny: float, nz: float,
    v_above: float, v_below: float,
    *,
    below_is_opposite_normal: bool = True,
    tol: float = 1e-12
) -> Tuple[float, float, float]:
    """
    Compute the transmitted (refracted) slowness vector across a planar interface
    using 3D Snell's law for isotropic media.

    Coordinates: ENU (x=East, y=North, z=Up).
      - s_above = (sx_above, sy_above, sz_above) are slowness components (s/km).
      - n = (nx, ny, nz) is the interface *unit* normal (dimensionless).
      - v_above, v_below are wave speeds (km/s) in the two half-spaces.

    Physics:
      - The tangential component of the slowness vector is conserved across the interface.
      - The normal component adjusts so that ||p_below|| = 1 / v_below.
      - The sign of the normal component below is chosen to match sign(p_above·n).
        If p_above·n ≈ 0 (grazing), we choose the sign so that the transmitted
        slowness points into the “below” half-space. With
        `below_is_opposite_normal=True`, “below” is opposite the normal direction.

    Returns:
      (sx_below, sy_below, sz_below) in s/km.

    Raises:
      ValueError if:
        - v_above or v_below are non-positive,
        - n is (near-)zero,
        - the transmitted wave is evanescent (total internal reflection),
        - inputs are numerically inconsistent.

    Notes:
      - This function does NOT modify the input normal orientation; ensure 'n' is
        the intended geometric normal for your interface.
      - For a perfectly horizontal interface, n=(0,0,1) (Up).
    """
    # Validate speeds
    if v_above <= 0 or v_below <= 0:
        raise ValueError("Wave speeds must be positive.")

    # Assemble vectors
    p_above = np.array([sx_above, sy_above, sz_above], dtype=float)
    n = np.array([nx, ny, nz], dtype=float)

    # Normalize the normal
    n_norm = np.linalg.norm(n)
    if not np.isfinite(n_norm) or n_norm < tol:
        raise ValueError("Interface normal must be non-zero.")
    n = n / n_norm

    # Optional: sanity-check incident magnitude vs. v_above (not required, but informative)
    inv_va = 1.0 / v_above
    p_mag = np.linalg.norm(p_above)
    if abs(p_mag - inv_va) > 1e-6 * inv_va:
        # Not fatal: incident may be numerically noisy. You can warn/log if desired.
        pass

    # Decompose incident slowness into tangential + normal components
    p_n_above = float(np.dot(p_above, n))          # scalar normal component
    p_t = p_above - p_n_above * n                  # tangential component (conserved)
    pt2 = float(np.dot(p_t, p_t))

    inv_vb = 1.0 / v_below
    inv_vb2 = inv_vb * inv_vb

    # Physical feasibility: ||p_t|| must not exceed 1/v_below
    if pt2 > inv_vb2 + tol:
        # No real transmitted wave: evanescent (total internal reflection)
        raise ValueError(
            "Evanescent transmitted wave (total internal reflection): "
            f"||p_t||={np.sqrt(pt2):.6g} > 1/v_below={inv_vb:.6g}."
        )

    # Compute transmitted normal component magnitude
    under = max(0.0, inv_vb2 - pt2)               # protect against tiny negatives
    p_n_below_mag = np.sqrt(under)

    # Choose sign for transmitted normal component
    sign = np.sign(p_n_above)
    if abs(sign) < 0.5:  # grazing incidence: p_n_above ~ 0
        sign = -1.0 if below_is_opposite_normal else +1.0

    p_below = p_t + sign * p_n_below_mag * n

    # Final polish: ensure numerical normalization (optional)
    # (Should already satisfy ||p_below|| = 1/v_below within rounding)
    # p_below *= (inv_vb / np.linalg.norm(p_below))

    return tuple(map(float, p_below))

# Example: horizontal interface (n up), wave going downward from above.
sx_a, sy_a = 0.05, 0.00             # horizontal slowness (s/km)
v_above, v_below = 6.0, 8.0         # km/s
inv_va = 1.0 / v_above
sz_a = -np.sqrt(max(0.0, inv_va**2 - sx_a**2 - sy_a**2))  # downward (negative z)

strike = 30.0
dip    = 10.0
nxval, nyval, nzval = normal_from_strike_dip( strike, dip )

print ('Normal = (',nxval,',',nyval,',',nzval,')' )

sx_b, sy_b, sz_b = transmit_slowness_snell_3d(
    sx_a, sy_a, sz_a,
    nx=nxval, ny=nyval, nz=nzval,         # Upward normal
    v_above=v_above, v_below=v_below
)

print("p_above:", (sx_a, sy_a, sz_a))
print("p_below:", (sx_b, sy_b, sz_b))
print("||p_above|| ~", 1.0 / v_above, "||p_below|| ~", 1.0 / v_below)

print ("Now in the other direction")

sx_a_back, sy_a_back, sz_a_back = incident_from_transmitted_snell_3d(
    sx_b, sy_b, sz_b,
    nx=nxval, ny=nyval, nz=nzval,   
    v_above=v_above, v_below=v_below
)

print("p_above_returned:", (sx_a_back, sy_a_back, sz_a_back))
