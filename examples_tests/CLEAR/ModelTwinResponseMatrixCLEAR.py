"""Make an RF-Track twin of a measured CLEAR response-matrix directory, to compare both in ComputeResponseMatrix_GUI.
Every DATA_*.pkl is copied with the same correctors [A] and quadrupoles [A]; only the BPM readings are replaced
by the model. Corrector calibration [T*mm/A] per family fitted to the Aug-Sep 2026 measurements (one value for all
sessions); the negative sign is the RF-Track convention for electrons.
Usage: python ModelTwinResponseMatrixCLEAR.py <measured_dir> [momentum_MeV_c=198]
Output: <measured_dir>_RFTrack"""
import glob, os, sys
import numpy as np
from machine_interfaces.Backend.State import State
from machine_interfaces_clear.InterfaceCLEAR_RFTrack import InterfaceCLEAR_RFTrack

CALIBRATION = {"DHG": -0.197, "DVG": -0.193, "DHJ": -0.436, "DVJ": -0.353}  # T*mm/A

src = os.path.abspath(os.path.expanduser(sys.argv[1]))
out = src + "_RFTrack"
os.makedirs(out, exist_ok=True)

sim = InterfaceCLEAR_RFTrack(nparticles=10)
sim.invert_bpm, sim.log = False, lambda *a: None
sim.Pref = float(sys.argv[2]) if len(sys.argv) > 2 else sim.Pref
sim._InterfaceCLEAR_RFTrack__setup_beam0()

for fp in sorted(glob.glob(f"{src}/DATA_*.pkl")):
    S = State(filename=fp)
    q = S.quadrupoles
    sim.set_quadrupoles(q["names"], q.get("iact", q["bact"]), track=False)
    kicks = {}
    for name, current in zip(S.correctors["names"], S.correctors["bact"]):
        kicks.setdefault(name.replace("DV", "DH"), [0.0, 0.0])["DV" in name] = CALIBRATION[name[3:6]] * current
    for name, kick in kicks.items():
        sim.lattice[name].set_strength(*kick)
    sim.lattice.track(sim.B0)
    b = sim.get_bpms(S.bpms["names"])
    S.bpms = {"names": b["names"], "x": b["x"], "y": b["y"], "tmit": b["tmit"]}
    S.interface_id = "machine_interfaces_clear.InterfaceCLEAR_RFTrack.InterfaceCLEAR_RFTrack"
    S.save(filename=os.path.join(out, os.path.basename(fp)))

print(f"Model twin written to {out}")
