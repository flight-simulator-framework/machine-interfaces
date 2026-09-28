import os
import tango
import time
from machine_interfaces_esrf.InterfaceESRF_TL2 import InterfaceESRF_TL2
os.environ["TANGO_HOST"] = "acs.esrf.fr:10000,acs.esrf.fr:11000"
v = os.getenv("TANGO_HOST")

print("-.-" * 17)
print(f"\tScript running on {v}")
print("-.-" * 17)

I = InterfaceESRF_TL2()

names = ['MAG.qf1']

for name in names:
    reading = tango.AttributeProxy(f"tl2/ps/{name.split('.')[-1]}/current").read()
    print(name, "Tango setpoint:", reading.w_value, "readback:", reading.value)

 
initial_current = I.get_quadrupoles(names)

print("Interface initial current:", initial_current)
 
I.set_quadrupoles(names, 52.0)

print("After changing quadrupoles with the interface:", I.get_quadrupoles(names))

print("Resetting back:", I.get_quadrupoles(names))

I.set_quadrupoles(names, initial_current["bact"])

print("Restored quadrupoles to initial values:", I.get_quadrupoles(names))
