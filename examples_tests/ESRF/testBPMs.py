import os
import tango
from machine_interfaces.Interfaces.ESRF.InterfaceESRF_TL2 import InterfaceESRF_TL2
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

names = ["BPM.cv1", "BPM.d2"]
device = tango.DeviceProxy("tl2/d-bpm/all")

print("Values obtained directly from Tango to check if the simple acquisition addresses work.")
print("Tango x:", device.x_position)
print("Tango y:", device.y_position)
print("Tango charge:", device.charge)
print("======Worked!======")

print("Test of ESRF interface method get_bpms().")
result = I.get_bpms(names)
for key, value in result.items():
    print(key, value)
print("get_bpms() works!")
