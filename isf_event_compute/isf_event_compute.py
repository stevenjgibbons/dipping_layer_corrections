#!/usr/bin/env python3
import sys
import math
from pathlib import Path

# ---------------------------
# Normalization helpers
# ---------------------------
def normalize_lon(lon_deg):
    """Normalize longitude to the range (-180, 180]."""
    return (lon_deg + 540) % 360 - 180

def normalize_az(az_deg):
    """Normalize azimuth to [0, 360)."""
    return az_deg % 360

def signed_circ_diff_deg(a_deg, b_deg):
    """Minimal signed difference a - b on the circle, in degrees, in (-180, 180]."""
    return ((a_deg - b_deg + 540.0) % 360.0) - 180.0

# ---------------------------
# Great-circle helpers (spherical Earth)
# ---------------------------
def forward_azimuth_station_to_event(statlat, statlon, evlat, evlon):
    """
    Forward azimuth from station -> event (degrees).
    Inputs/outputs in degrees. Uses spherical Earth great-circle formula.
    """
    φ1 = math.radians(statlat)
    λ1 = math.radians(statlon)
    φ2 = math.radians(evlat)
    λ2 = math.radians(evlon)
    dλ = λ2 - λ1
    # α = atan2( sin(dλ)*cos φ2, cos φ1*sin φ2 − sin φ1*cos φ2*cos dλ )
    y = math.sin(dλ) * math.cos(φ2)
    x = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(dλ)
    α = math.atan2(y, x)  # radians
    return normalize_az(math.degrees(α))

def backazimuth_event_to_station(statlat, statlon, evlat, evlon):
    """
    'Backazimuth' in seismological usage: direction at the *event* toward the station.
    On a sphere, this equals the forward azimuth event->station.
    """
    return forward_azimuth_station_to_event(evlat, evlon, statlat, statlon)

def az_event_to_station(statlat, statlon, evlat, evlon):
    """
    Convenience wrapper for clarity where we want azimuth measured at the event
    pointing back to the station (event -> station).
    """
    return forward_azimuth_station_to_event(evlat, evlon, statlat, statlon)

def forward_point_from_station(statlat, statlon, dist_deg, az_stn_to_ev_deg):
    """
    Given station (deg), great-circle distance Δ (deg), and forward azimuth α (deg)
    measured at the station toward the event, return the event (lat, lon) in degrees.
    Spherical forward geodesic:
    φ2 = asin( sinφ1 cosΔ + cosφ1 sinΔ cosα )
    λ2 = λ1 + atan2( sinα sinΔ cosφ1, cosΔ − sinφ1 sinφ2 )
    """
    φ1 = math.radians(statlat)
    λ1 = math.radians(statlon)
    Δ = math.radians(dist_deg)
    α = math.radians(normalize_az(az_stn_to_ev_deg))
    sinφ2 = math.sin(φ1) * math.cos(Δ) + math.cos(φ1) * math.sin(Δ) * math.cos(α)
    φ2 = math.asin(sinφ2)
    λ2 = λ1 + math.atan2(
        math.sin(α) * math.sin(Δ) * math.cos(φ1),
        math.cos(Δ) - math.sin(φ1) * sinφ2
    )
    return math.degrees(φ2), normalize_lon(math.degrees(λ2))

# ---------------------------
# Epicenter from station with 1-D azimuth search (replacement)
# ---------------------------
def earthquake_from_station(statlat, statlon, dist_deg, az_eq_to_stn_deg):
    """
    Improved solver:
    - We *search* the unknown station->event azimuth that best reproduces the
      given earthquake->station azimuth (az_eq_to_stn_deg) when evaluated at
      the trial event location.
    - Coarse grid (0.1°) over [0, 360), then refine (0.01°) in a ±2° window.
    Inputs:
      statlat, statlon : station coordinates (deg)
      dist_deg : epicentral distance (deg)
      az_eq_to_stn_deg : azimuth measured at the *event* toward the station (deg)
    Returns:
      (evlat, evlon) in degrees
    """
    az_ev_to_stn_target = normalize_az(az_eq_to_stn_deg)
    best_err, best_az = 1e9, None
    best_lat_e, best_lon_e = None, None

    # Coarse then refine
    for step in (0.1, 0.01):
        start = 0.0 if best_az is None else max(0.0, best_az - 2.0)
        stop  = 360.0 if best_az is None else min(360.0, best_az + 2.0)
        a = start
        while a <= stop + 1e-12:
            # Trial event for station->event azimuth = a
            lat_e, lon_e = forward_point_from_station(statlat, statlon, dist_deg, a)
            # Predicted azimuth at event back to station
            az21 = az_event_to_station(statlat, statlon, lat_e, lon_e)
            # Circular absolute difference in degrees
            err = abs(((az21 - az_ev_to_stn_target + 540.0) % 360.0) - 180.0)
            if err < best_err:
                best_err, best_az = err, a
                best_lat_e, best_lon_e = lat_e, lon_e
            a += step

    # Return the best event location found
    return best_lat_e, best_lon_e

# ---------------------------
# Parsing & computation
# ---------------------------
def parse_line(line):
    """
    Parse one input line.
    Expected tokens (example):
      0: station
      1: dist_deg
      2: az_eq_to_stn_deg
      3: phase (e.g., 'P') <-- often present in examples
      4: arrival time ISO8601
      5: baz (measured, station->event direction)
      6: slowness (s/deg)
      7: SNR
      8: earthquake ID
      9: arrival ID
      10: statlat
      11: statlon
    To be robust, we anchor the trailing fields from the end and read dist/az from the front.
    """
    toks = line.split()
    if len(toks) < 11:
        raise ValueError("Too few tokens")

    station = toks[0]
    dist_deg = float(toks[1])
    az_eq_to_stn_deg = float(toks[2])

    # From the end (robust if a phase token exists in the middle)
    statlon = float(toks[-1])
    statlat = float(toks[-2])
    arrival_id = toks[-3]
    earthquake_id = toks[-4]
    snr = float(toks[-5])
    sl_sec_per_deg = float(toks[-6])
    baz = float(toks[-7])  # measured at station toward event
    arrival_time = toks[-8]  # keep as string

    return {
        "station": station,
        "dist_deg": dist_deg,
        "az_eq_to_stn_deg": az_eq_to_stn_deg,
        "arrival_time": arrival_time,
        "baz": baz,
        "sl_sec_per_deg": sl_sec_per_deg,
        "snr": snr,
        "earthquake_id": earthquake_id,
        "arrival_id": arrival_id,
        "statlat": statlat,
        "statlon": statlon,
        "raw": line.rstrip("\n")
    }

def compute_row(fields):
    """
    Given parsed fields, compute evlat/evlon (via the search solver), azimuths,
    slowness metrics, and component slownesses (sx, sy).
    """
    statlat = fields["statlat"]
    statlon = fields["statlon"]
    dist_deg = fields["dist_deg"]
    az_eq_to_stn_deg = fields["az_eq_to_stn_deg"]
    baz_meas = fields["baz"]
    s_per_deg = fields["sl_sec_per_deg"]

    # Event location via improved azimuth-search solver
    evlat, evlon = earthquake_from_station(statlat, statlon, dist_deg, az_eq_to_stn_deg)

    # Azimuths based on the computed event position
    az_stn_to_ev = forward_azimuth_station_to_event(statlat, statlon, evlat, evlon)
    baz_ev_to_stn = backazimuth_event_to_station(statlat, statlon, evlat, evlon)

    # New: signed circular difference (measured - true)
    baz_minus_true = signed_circ_diff_deg(baz_meas, az_stn_to_ev)

    # Slowness conversions and derived quantities
    # 1 deg ~ 111.12 km (approx)
    sl_sec_per_km = s_per_deg / 111.12 if s_per_deg is not None else float("nan")
    appvel = float("inf") if sl_sec_per_km == 0 else (1.0 / sl_sec_per_km)

    # Component slownesses from measured baz (clockwise from North):
    # sx (W->E) = s * sin(baz), sy (S->N) = s * cos(baz)
    baz_rad = math.radians(baz_meas)
    sx_measured = sl_sec_per_km * math.sin(baz_rad)
    sy_measured = sl_sec_per_km * math.cos(baz_rad)

    return {
        "evlat": evlat,
        "evlon": evlon,
        "az_stn_to_ev": az_stn_to_ev,
        "baz_ev_to_stn": baz_ev_to_stn,
        "appvel": appvel,
        "sx_measured": sx_measured,
        "sy_measured": sy_measured,
        "baz_minus_true": baz_minus_true,
    }

def format_append(computed):
    """
    Format the eight values as right-justified fixed-width fields:
      evlat (10.4f), evlon (11.4f),
      az_stn_to_ev (8.2f), baz_ev_to_stn (8.2f),
      appvel (8.2f),
      sx_measured (11.6f), sy_measured (11.6f),
      (baz_meas - az_stn_to_ev) (8.2f)
    Adjust widths here if you prefer different alignment.
    """
    return (
        f"{computed['evlat']:10.4f}"
        f"{computed['evlon']:11.4f}"
        f"{computed['az_stn_to_ev']:8.2f}"
        f"{computed['baz_ev_to_stn']:8.2f}"
        f"{computed['appvel']:8.2f}"
        f"{computed['sx_measured']:11.6f}"
        f"{computed['sy_measured']:11.6f}"
        f"{computed['baz_minus_true']:8.2f}"
    )

def derive_output_path(in_path: Path) -> Path:
    """Insert '_event' before the .txt suffix (or append if no .txt)."""
    if in_path.suffix.lower() == ".txt":
        return in_path.with_name(in_path.stem + "_event" + in_path.suffix)
    else:
        return in_path.with_name(in_path.name + "_event.txt")

def main():
    if len(sys.argv) != 2:
        print("Usage: python isf_event_compute.py <input_file.txt>")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    if not in_path.exists():
        print(f"Error: input file not found: {in_path}")
        sys.exit(2)

    out_path = derive_output_path(in_path)
    n_in = n_out = n_err = 0

    with in_path.open("r", encoding="utf-8", errors="replace") as fin, \
         out_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            n_in += 1
            if not line.strip():
                fout.write(line)
                continue
            try:
                fields = parse_line(line)
                computed = compute_row(fields)
                fout.write(fields["raw"] + format_append(computed) + "\n")
                n_out += 1
            except Exception as e:
                # Preserve the original line; also write a comment line with the error.
                fout.write(line.rstrip("\n") + " # parse/compute error: " + str(e) + "\n")
                n_err += 1

    print(f"Done. Lines read: {n_in}, written: {n_out}, with warnings: {n_err}")
    print(f"Output: {out_path}")

if __name__ == "__main__":
    main()
