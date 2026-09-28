import os, sys, pyjapc, time
import pyda, pyda_japc
from pathlib import Path
import numpy as np
from machine_interfaces_clear.InterfaceCLEAR import CLEAR_real_machine
import matplotlib.pyplot as plt

I = CLEAR_real_machine()

client = pyda.SimpleClient(provider=pyda_japc.JapcProvider())
context_acquisition = "SCT.USER.SETUP"
context_empty = ""

#
# steps_readback_position = client.get('CO.TOWB.102.UVATT2/Setting').data['position']
# steps_readback_position_min = client.get('CO.TOWB.102.UVATT2/Setting').data['position_min']
# steps_readback_position_max = client.get('CO.TOWB.102.UVATT2/Setting').data['position_max']
#
# # prints:
# # position_min
# # position_max
# # position
#
# print(steps_readback_position)
# print(steps_readback_position_min)
# print(steps_readback_position_max)


print("Calling change_intensity...")
I.change_intensity()
print("Called change_intensity. Starting to reset...")
time.sleep(25)

I.reset_intensity()
print("Called reset_intensity.")


