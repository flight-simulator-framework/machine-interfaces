import os
import tango
from machine_interfaces.Interfaces.ESRF.InterfaceESRF_TL2 import InterfaceESRF_TL2

print("TANGO_HOST:", os.getenv("TANGO_HOST"))
I = InterfaceESRF_TL2()

names = ['MAG.qf1']
delta = None
for name in names:
    reading = tango.AttributeProxy(f"tl2/ps/{name.split('.')[-1]}/current").read()
    print(name, "Tango setpoint:", reading.w_value, "readback:", reading.value)

initial = I.get_quadrupoles(names)
print("Interface:", initial)
if delta is not None:
    try:
        I.set_quadrupoles(names, initial["bdes"] + delta)
        print("After change:", I.get_quadrupoles(names))
    finally:
        I.set_quadrupoles(names, initial["bdes"])
        print("Restored:", I.get_quadrupoles(names))
