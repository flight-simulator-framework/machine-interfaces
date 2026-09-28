import os
import tango
from machine_interfaces_esrf.InterfaceESRF_TL2 import InterfaceESRF_TL2
from machine_interfaces.Backend.State import State
from matplotlib import pyplot as plt


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
device = tango.DeviceProxy("tl2/d-bpm/all")

print("Values obtained directly from Tango to check if the simple acquisition addresses work.")
print("Tango x:", device.x_position)
print("Tango y:", device.z_position)
print("Tango charge:", device.charge)
print("======Worked!======")

print("Test of ESRF interface method get_bpms().")
result = I.get_bpms()
state = State(bpms=result)
orbit = state.get_orbit()

plt.errorbar(orbit["names"], orbit["x"], yerr=orbit["stdx"], fmt="o-", label="x")
plt.errorbar(orbit["names"], orbit["y"], yerr=orbit["stdy"], fmt="o-", label="y")
plt.xlabel("BPM")
plt.ylabel("Position")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

for key, value in result.items():
    print(key, value)
print("get_bpms() works!")
