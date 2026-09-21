import os
import tango
from machine_interfaces.Interfaces.ESRF.InterfaceESRF_TL2 import InterfaceESRF_TL2

print("TANGO_HOST:", os.getenv("TANGO_HOST"))
I = InterfaceESRF_TL2()

delta = None
attribute = tango.AttributeProxy("elin/beam/run/gridv")
print("Grid voltage [V]:", attribute.read().w_value)
print("Charge:", I.get_icts(I.chosen_ict))
if delta is not None:
    try:
        I.change_intensity(delta)
        print("After change [V]:", attribute.read().w_value)
        print("Charge:", I.get_icts(I.chosen_ict))
    finally:
        I.reset_intensity()
        print("Restored [V]:", attribute.read().w_value)
