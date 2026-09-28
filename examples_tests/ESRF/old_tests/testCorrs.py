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

names = ['COR.ch1', 'COR.cv1']
print("Values obtained directly from Tango to check if the simple acquisition addresses work.")
for name in names:
    reading = tango.AttributeProxy(f"tl2/ps-c1/{name.split('.')[-1]}/current").read()
    print(name, "Tango setpoint:", reading.w_value, "readback:", reading.value)
print("======Worked!======")


print("Test of ESRF interface method get_correctors().")
initial_state = I.get_correctors(names)
print(initial_state)

print("Test of ESRF interface method set_correctors().")
I.set_correctors(names, 10.0) # adjust the number!!!
print("After change:", I.get_correctors(names))

I.set_correctors(names, initial_state["bdes"])
print("Restored:", I.get_correctors(names))
