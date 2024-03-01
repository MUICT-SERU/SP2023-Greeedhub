"""
Dans_Diffraction Examples
Plot powder patter from crystal
"""

import sys,os
import numpy as np
import matplotlib.pyplot as plt # Plotting
import Dans_Diffraction as dif

cf=os.path.dirname(__file__)


f = cf+'/../Dans_Diffraction/Structures/Diamond.cif'

xtl = dif.Crystal(f)

xtl.Plot.simulate_powder(energy_kev=8, peak_width=0.01, background=0)
plt.show()