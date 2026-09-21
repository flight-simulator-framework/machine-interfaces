import os
import tango
from machine_interfaces.Interfaces.ESRF.InterfaceESRF_TL2 import InterfaceESRF_TL2

print("TANGO_HOST:", os.getenv("TANGO_HOST"))
I = InterfaceESRF_TL2()

print("Sequence:", I.get_sequence())
print("H correctors:", I.get_hcorrectors_names())
print("V correctors:", I.get_vcorrectors_names())
state = I.get_state()
print("Correctors:", state.get_correctors())
print("BPMs:", state.get_bpms())
print("ICTs:", state.get_icts())
print("Quadrupoles:", state.get_quadrupoles())
