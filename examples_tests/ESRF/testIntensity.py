import os
import tango
import time
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

attribute = tango.AttributeProxy("elin/beam/run/gridv")

I.change_intensity()
print("After change [V]:", attribute.read().w_value)
print("Charge:", I.get_icts(I.chosen_ict))
time.sleep(5)
I.reset_intensity()
print("Restored [V]:", attribute.read().w_value)
