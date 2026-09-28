import os
# import time
import tango
from machine_interfaces_esrf.InterfaceESRF_TL2 import InterfaceESRF_TL2

I = InterfaceESRF_TL2()

# I.reset_energy()
# exit()

 
print("Values obtained directly from Tango to check if the simple acquisition addresses work.")

attribute = tango.AttributeProxy("infra/t-whist/bunchclock/Text")

print("Text:", attribute.read().w_value)

print("======Worked!======")


print("Test of ESRF interface method change_energy().")

print("dP/P:", I.change_energy(0.0)) # millis
# time.sleep(5)

print("After change:", attribute.read().w_value)

I.reset_energy()
print("Restored:", attribute.read().w_value)
