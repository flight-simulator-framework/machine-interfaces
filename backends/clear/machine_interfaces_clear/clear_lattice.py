import os, re, tempfile, urllib.request
import RF_Track as rft
from cpymad.madx import Madx

URL = "https://gitlab.cern.ch/acc-models/acc-models-clear/-/raw/master/"
LOCAL = os.path.join(os.path.dirname(__file__), "Setup_files", "clear_to_rftrack")
# Nominal quadrupole currents [A], as in acc-models madxTesting/test.madx
QUAD_CURRENTS = "ca.iqfd0350=47.5; ca.iqdd0355=86.4; ca.iqfd0360=59.0; ca.iqfd0510=44.0; ca.iqdd0515=71.8; ca.iqfd0520=38.8; ca.iqfd0760=61.0; ca.iqdd0765=97.9; ca.iqfd0770=53.0;"
# Upstream of CA.QFD0350 only correctors and accelerating structures are modelled
INJECTOR_KEEP = re.compile(r"CA\.(DHG|SDV|ACS)\d{4}")


def _read(path, online):
    if online:
        return urllib.request.urlopen(URL + path, timeout=5).read().decode()
    with open(os.path.join(LOCAL, os.path.basename(path))) as f:
        return f.read()


def _trim_injector(full):
    lattice, gap, prev, injector = rft.Lattice(), 0.0, None, True
    for element in full['*']:
        name = element.get_name()
        injector &= name != "CA.QFD0350"
        if injector and not INJECTOR_KEEP.fullmatch(name):
            gap += element.get_length()
            continue
        if prev and gap:
            drift = rft.Drift(gap)
            drift.set_name(f"GAP_{prev}_{name.removeprefix('CA.')}")
            lattice.append(drift)
        lattice.append(element)
        gap, prev = 0.0, name.removeprefix('CA.')
    return lattice


def _build(online):
    with tempfile.TemporaryDirectory() as tmp, Madx(stdout=False) as madx:
        tfs = os.path.join(tmp, "clear.tfs")
        madx.input(_read("beams/standard.beam", online) + _read("clear.seqx", online) + QUAD_CURRENTS)
        madx.use(sequence="CLEARLINE")
        madx.select(flag="twiss", full=True)
        madx.twiss(beta0="initbeta0", file=tfs)
        return _trim_injector(rft.Lattice(tfs))


def load_clear_lattice():
    """CLEAR lattice from the latest acc-models master, or from the local copy if that fails."""
    try:
        return _build(online=True)
    except Exception as e:
        print(f"Latest CLEAR model from acc-models unavailable ({e}), using local copy")
        return _build(online=False)
