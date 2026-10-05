"""Old CLEAR states (Aug 2026) kept K1L [1/m] in quadrupoles bdes/bact and the current in ides/iact, without value_unit.
Rewrite them to the current format: bdes/bact in A, value_unit "A". The K1L values are kept as bdes_K1L/bact_K1L.
Usage: python ConvertQuadK1LToAmps.py [root] [--dry-run]"""
import glob, gzip, os, pickle, sys

root = next((a for a in sys.argv[1:] if not a.startswith("--")), os.path.expanduser("~/CERN-Flight_Simulator-Data/AllCLEARfiles/Quadrupole_Scans"))
dry_run = "--dry-run" in sys.argv

converted = 0
for path in sorted(glob.glob(f"{root}/**/screen_*_step_*_shot_*.pkl", recursive=True)):
    with open(path, "rb") as f:
        is_gzip = f.read(2) == b"\x1f\x8b"
    opener = gzip.open if is_gzip else open
    with opener(path, "rb") as f:
        state = pickle.load(f)
    quads = state["quadrupoles"]
    if "value_unit" in quads or "ides" not in quads:
        continue
    quads.update(bdes_K1L=quads["bdes"], bact_K1L=quads["bact"], bdes=quads["ides"], bact=quads["iact"], value_unit="A")
    converted += 1
    if dry_run:
        continue
    with opener(path + ".tmp", "wb") as f:
        pickle.dump(state, f)
    os.replace(path + ".tmp", path)

print(f"{'Would convert' if dry_run else 'Converted'} {converted} files in {root}")
