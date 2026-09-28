import os
import tango
from machine_interfaces_esrf.InterfaceESRF_TL2 import InterfaceESRF_TL2
os.environ["TANGO_HOST"] = "ebs-simu-1:10000"
v = os.getenv("TANGO_HOST")
if v == "ebs-simu-1:10000":
    simulator = True
else:
    simulator = False

print("-.-" * 17)
print(f"\tScript running on {v}")
print("-.-" * 17)

I = InterfaceESRF_TL2()

print("Tango BPM charge:", tango.DeviceProxy("tl2/d-bpm/all").charge)
print("Tango ICT charge:", tango.DeviceProxy(I.chosen_ict).totalcharge)
print("Interface:", I.get_icts())
print("Selected BPM:", I.get_icts("BPM.d2"))
print("Selected ICT:", I.get_icts(I.chosen_ict))
