import os
import tango
import time
from machine_interfaces_esrf.InterfaceESRF_TL2 import InterfaceESRF_TL2


I = InterfaceESRF_TL2()
 
attribute = tango.AttributeProxy("elin/beam/run/pulsev") 

print("Charge before:", I.get_icts(I.chosen_ict))

I.change_intensity(-1.0)

print("After change [V]:", attribute.read().w_value)

print("Charge:", I.get_icts(I.chosen_ict))

time.sleep(5)

I.reset_intensity()

print("Restored [V]:", attribute.read().w_value)
