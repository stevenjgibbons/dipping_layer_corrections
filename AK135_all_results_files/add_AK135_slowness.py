#!/usr/bin/env python3
import sys
import os
import math
from obspy.taup import TauPyModel


def dist_deg(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi/2)**2 +
         math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2)
    return math.degrees(2 * math.asin(math.sqrt(a)))


def station_to_event_azimuth(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)

    y = math.sin(dlambda) * math.cos(phi2)
    x = (math.cos(phi1)*math.sin(phi2) -
         math.sin(phi1)*math.cos(phi2)*math.cos(dlambda))

    az = math.degrees(math.atan2(y, x))
    return az % 360.0


def extract_p_s_per_km(arr):
    """
    Extract ray parameter in s/km, compatible with ALL ObsPy versions.
    """
    # Newer ObsPy
    if hasattr(arr, "ray_param_sec_per_km"):
        return arr.ray_param_sec_per_km

    # Common older builds: s/radian
    EARTH_RADIUS_KM = 6371.0

    if hasattr(arr, "ray_param_sec"):
        return arr.ray_param_sec / EARTH_RADIUS_KM

    if hasattr(arr, "ray_param"):
        return arr.ray_param / EARTH_RADIUS_KM

    return None


def pick_arrival(model, ddeg, phase_raw):
    """
    Implements EXACT statphase2slowvec.py logic:
    P1 = first arrival whose name starts with 'P'
    S1 = first arrival whose name starts with 'S'
    Otherwise: specific phase.
    """

    ph0 = phase_raw[0].upper()

    # ---- P1 logic ----
    if ph0 == "P":
        arrivals = model.get_travel_times(0.0, ddeg)
        for arr in arrivals:
            if arr.name.startswith("P"):
                return extract_p_s_per_km(arr)
        return None

    # ---- S1 logic ----
    elif ph0 == "S":
        arrivals = model.get_travel_times(0.0, ddeg)
        for arr in arrivals:
            if arr.name.startswith("S"):
                return extract_p_s_per_km(arr)
        return None

    # ---- Specific phase ----
    arrivals = model.get_travel_times(0.0, ddeg, phase_list=[phase_raw])
    if not arrivals:
        return None
    return extract_p_s_per_km(arrivals[0])


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_AK135_slowness.py STATION")
        sys.exit(1)

    station = sys.argv[1]

    indir = "../collect_all_results_files"
    infile = f"{indir}/{station}_all_arrivals.txt"
    outfile = f"./{station}_all_arrivals_with_AK135sxsy.txt"

    if not os.path.exists(infile):
        print(f"Input file not found: {infile}")
        sys.exit(2)

    model = TauPyModel("ak135")

    with open(infile) as fin, open(outfile, "w") as fout:
        for line in fin:
            raw = line.rstrip("\n")
            if not raw.strip():
                continue

            toks = raw.split()
            if len(toks) < 14:
                fout.write(raw + "\n")
                continue

            phase_raw = toks[3]
            stat_lat = float(toks[10])
            stat_lon = float(toks[11])
            ev_lat   = float(toks[12])
            ev_lon   = float(toks[13])

            ddeg = dist_deg(stat_lat, stat_lon, ev_lat, ev_lon)
            az = station_to_event_azimuth(stat_lat, stat_lon, ev_lat, ev_lon)

            p = pick_arrival(model, ddeg, phase_raw)

            if p is None:
                sx = float("nan")
                sy = float("nan")
            else:
                azr = math.radians(az)
                #No we are already in this direction sx = -p * math.sin(azr)   # W->E
                #No we are already in this direction sy = -p * math.cos(azr)   # S->N
                sx = p * math.sin(azr)   # W->E
                sy = p * math.cos(azr)   # S->N

            fout.write(f"{raw}{sx:15.6f}{sy:15.6f}\n")

    print(f"Written: {outfile}")


if __name__ == "__main__":
    main()
