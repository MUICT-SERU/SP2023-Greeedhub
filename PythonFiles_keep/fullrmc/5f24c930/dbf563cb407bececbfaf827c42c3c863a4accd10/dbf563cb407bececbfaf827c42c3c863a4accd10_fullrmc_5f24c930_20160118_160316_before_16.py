# USAGE: python setup.py build_ext --inplace

# standard libraries imports
import os
import warnings
import shutil
from distutils.core import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

# external libraries imports
import numpy as np

# fullrmc imports
from fullrmc.Core.Collection import get_path

# general variables
fullrmc_PATH     = get_path("fullrmc")
CURRENT_PATH     = os.path.abspath(os.path.dirname(__file__))
EXTENSIONS_PATH  = os.path.join(fullrmc_PATH, "Extensions")
DESTINATION_PATH = os.path.join(fullrmc_PATH, "Core")

## get .pyx modules names
#pyxModules = [fname for fname in os.listdir(EXTENSIONS_PATH)]
## setup modules
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"get_reciprocal_basis.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"transform_coordinates.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"pair_distribution_histogram.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"distances.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"bonds.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"angles.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"improper_angles.pyx")),
#       include_dirs=[np.get_include()] )
#setup( ext_modules = cythonize(os.path.join(fullrmc_PATH,"atomic_coordination_number.pyx"),language="c++"),
#       include_dirs=[np.get_include()] )


c_cpp = [# get_reciprocal_basis
         #Extension('get_reciprocal_basis',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"get_reciprocal_basis.c")]),
         ## transform_coordinates
         #Extension('transform_coordinates',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"transform_coordinates.c")]),
         ## pair_distribution_histogram
         #Extension('pair_distribution_histogram',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"pair_distribution_histogram.c")]),
         ## distances
         #Extension('distances',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"distances.c")]),
         ## bonds
         #Extension('bonds',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"bonds.c")]),
         ## angles
         #Extension('angles',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"angles.c")]),
         ## improper_angles
         #Extension('improper_angles',
         #include_dirs=[np.get_include()],
         #sources = [os.path.join(EXTENSIONS_PATH,"improper_angles.c")]),
         ## atomic_coordination_number
         #Extension('atomic_coordination_number',
         #include_dirs=[np.get_include()],
         #language="c++",
         #sources = [os.path.join(EXTENSIONS_PATH,"atomic_coordination_number.cpp")]),
        ]

pyx = [# get_reciprocal_basis
       Extension('get_reciprocal_basis',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"get_reciprocal_basis.pyx")]),
       # transform_coordinates
       Extension('transform_coordinates',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"transform_coordinates.pyx")]),
       # pair_distribution_histogram
       Extension('pair_distribution_histogram',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"pair_distribution_histogram.pyx")]),
       # distances
       Extension('distances',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"distances.pyx")]),
       # bonds
       Extension('bonds',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"bonds.pyx")]),
       # angles
       Extension('angles',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"angles.pyx")]),
       # improper_angles
       Extension('improper_angles',
       include_dirs=[np.get_include()],
       sources = [os.path.join(EXTENSIONS_PATH,"improper_angles.pyx")]),
       # atomic_coordination_number
       Extension('atomic_coordination_number',
       include_dirs=[np.get_include()],
       language="c++",
       sources = [os.path.join(EXTENSIONS_PATH,"atomic_coordination_number.pyx")]),
       ]

# setup all c and cpp files
setup( ext_modules = c_cpp)

# setup all pyx files
setup( ext_modules = pyx, 
       cmdclass = {'build_ext': build_ext} )
       
# copy all compiled files to fullrmc.Core
for fname in os.listdir('.'):#EXTENSIONS_PATH):
    if (".so" not in fname) and (".pyd" not in fname):
        continue
    # try to copy
    try:
        #shutil.copy(os.path.join(EXTENSIONS_PATH,fname), os.path.join(DESTINATION_PATH,fname))
        shutil.move(os.path.join('.',fname), os.path.join(DESTINATION_PATH,fname))
    except Exception as e:
        warnings.warn("Unable to copy compiled file '%s'. Try recompiling as admin (%s)"%(fname,e))
    
    
