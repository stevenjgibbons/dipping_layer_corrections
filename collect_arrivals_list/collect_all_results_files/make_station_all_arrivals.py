#!/usr/bin/env python3
import sys
import glob
import os

def load_ignore_list(filename: str):
    """Load phases to ignore (substring match, case-insensitive)."""
    ignore = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    ignore.append(s.lower())
    except FileNotFoundError:
        print(f"Warning: ignore file '{filename}' not found — no phases ignored.")
    return ignore

def phase_class(phase: str):
    """
    Return 'P' if phase starts with 'P'/'p',
           'S' if phase starts with 'S'/'s',
           None otherwise.
    """
    if not phase:
        return None
    c = phase[0].lower()
    if c == 'p':
        return 'P'
    if c == 's':
        return 'S'
    return None

def should_ignore(phase: str, ignore_list):
    """Return True if phase contains any ignore token."""
    pl = phase.lower()
    return any(tok in pl for tok in ignore_list)

def main():
    if len(sys.argv) != 2:
        print("Usage: python make_station_all_arrivals.py STATION")
        sys.exit(1)

    station = sys.argv[1]

    # --- Load ignore list ---
    ignore_file = "phases_to_ignore.txt"
    ignore_list = load_ignore_list(ignore_file)
    if ignore_list:
        print("Ignoring phases containing:", ignore_list)

    # --- Input files ---
    in_pattern = f"../{station}/{station}_*_filt_event.txt"
    files = sorted(glob.glob(in_pattern))

    if not files:
        print(f"No input files found: {in_pattern}")
        sys.exit(2)

    # Dictionary eventID -> {'P': first_P_line, 'S': first_S_line}
    seen = {}
    kept_records = []

    for fname in files:
        try:
            with open(fname, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    raw = line.rstrip("\n")
                    if not raw.strip():
                        continue

                    toks = raw.split()
                    if len(toks) < 9:
                        continue

                    phase = toks[3]
                    eid = toks[8]

                    # ignore list check (substring match)
                    if should_ignore(phase, ignore_list):
                        continue

                    cls = phase_class(phase)
                    if cls is None:
                        continue

                    slot = seen.setdefault(eid, {})

                    if cls not in slot:
                        slot[cls] = raw
                        kept_records.append(raw)

        except OSError as e:
            print(f"Warning: could not read {fname}: {e}")

    # --- Output file ---
    out_dir = os.path.join("..", station)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{station}_all_arrivals.txt")

    with open(out_path, "w", encoding="utf-8") as out:
        for rec in kept_records:
            out.write(rec + "\n")

    # Small summary
    total_events = len(seen)
    num_p = sum(1 for v in seen.values() if 'P' in v)
    num_s = sum(1 for v in seen.values() if 'S' in v)

    print(f"\nWrote: {out_path}")
    print(f"Events: {total_events}  |  kept P: {num_p}  |  kept S: {num_s}")

if __name__ == "__main__":
    main()
