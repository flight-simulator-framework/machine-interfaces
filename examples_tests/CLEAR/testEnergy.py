import os, sys, pyjapc, time
import pyda, pyda_japc
from pathlib import Path
import numpy as np
from machine_interfaces.Interfaces.CLEAR.InterfaceCLEAR import CLEAR_real_machine
import matplotlib.pyplot as plt

I = CLEAR_real_machine()

client = pyda.SimpleClient(provider=pyda_japc.JapcProvider())
context_acquisition = "SCT.USER.SETUP"
context_empty = ""

# energy_readback =client.get('CK.LL-MKS11/Setting')
#energy_readback =client.get('CK.LL-MKS15/Setting')
#PhaseSh_Sp to be checked but it's probably what we want to change

print("Change energy method")
energy_readback = I.change_energy()
print(energy_readback)
print("Change energy method finished")
print("Reset energy method")
I.reset_energy()
print("Reset energy finished")

