import os
import tango
from machine_interfaces.Interfaces.ESRF.InterfaceESRF_TL2 import InterfaceESRF_TL2

print("TANGO_HOST:", os.getenv("TANGO_HOST"))
I = InterfaceESRF_TL2()

print("Tango BPM charge:", tango.DeviceProxy("tl2/d-bpm/all").charge)
print("Tango ICT charge:", tango.DeviceProxy(I.chosen_ict).totalcharge)
print("Interface:", I.get_icts())
print("Selected BPM:", I.get_icts("BPM.d2"))
print("Selected ICT:", I.get_icts(I.chosen_ict))
