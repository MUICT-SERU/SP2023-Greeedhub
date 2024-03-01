"""
Dans_Diffraction Examples
Calculate list of reflections
"""

import sys,os
import numpy as np
import matplotlib.pyplot as plt # Plotting
import Dans_Diffraction as dif

cf=os.path.dirname(__file__)


f = cf+'/../Dans_Diffraction/Structures/Ca2RuO4.cif'

xtl = dif.Crystal(f)
xtl.Atoms.changeatom(1,mxmymz=[1,3,0])
xtl.generate_structure()

F0,F1,F2 = 0,1,1
HKLs = [[1,0,0],[2,0,0]]
inten=xtl.Scatter.xray_resonant(HKLs, energy_kev=2.967,azim_zero=[0,0,1],PSI=[90],F0=F0,F1=F1,F2=F2)

xtl.Plot.simulate_azimuth([1,0,0], energy_kev=2.967, polarisation='sp', azim_zero=[0,1,0])
plt.show()