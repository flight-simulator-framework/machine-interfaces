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

print("Values obtained directly from Tango to check if the simple acquisition addresses work.")
attribute = tango.AttributeProxy("infra/t-whist/bunchclock/Text")
print("Text:", attribute.read().w_value)
print("======Worked!======")

print("Test of ESRF interface method change_energy().")
print("dP/P:", I.change_energy(0.002)) # it's in ms
print("After change:", attribute.read().w_value)
I.reset_energy()
print("Restored:", attribute.read().w_value)
