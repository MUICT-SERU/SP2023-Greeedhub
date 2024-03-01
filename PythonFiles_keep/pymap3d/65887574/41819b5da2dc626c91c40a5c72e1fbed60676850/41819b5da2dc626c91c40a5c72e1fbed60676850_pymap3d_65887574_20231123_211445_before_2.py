#!/usr/bin/env python3
from __future__ import annotations

import logging
from datetime import datetime

import numpy as np

from pymap3d.eci import ecef2eci, eci2ecef

from matlab_aerospace import matlab_aerospace
from matlab_engine import matlab_engine


ecef = [-5762640.0, -1682738.0, 3156028.0]
utc = datetime(2019, 1, 4, 12)

eci_py = ecef2eci(ecef[0], ecef[1], ecef[2], utc)

eng = matlab_engine()

utc_matlab = eng.datetime(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second)
if matlab_aerospace(eng):
    eci_matlab = eng.ecef2eci(utc_matlab, np.asarray(ecef), nargout=1)
else:
    eci_matlab = eng.matmap3d.ecef2eci(utc_matlab, *ecef, nargout=3)

eci_m = np.array(eci_matlab.tomemoryview()).reshape(eci_matlab.size, order="F")

eci_good = np.isclose(eci_py, eci_m, rtol=0.01).all()

if eci_good:
    print("OK: PyMap3d ecef2eci vs. Matlab ecef2eci")
else:
    logging.error(f"eci2ecef did not match Matlab  {eci_py}  !=  {eci_matlab}")

ecef_py = eci2ecef(eci_m[0], eci_m[1], eci_m[2], utc)

if matlab_aerospace(eng):
    ecef_matlab = eng.eci2ecef(utc_matlab, eci_m, nargout=1)
else:
    ecef_matlab = eng.matmap3d.eci2ecef(utc_matlab, *eci_m, nargout=3)

ecef_m = np.array(ecef_matlab.tomemoryview()).reshape(ecef_matlab.size, order="F")

ecef_good = np.isclose(ecef_py, ecef_m, rtol=0.02).all()

if ecef_good:
    print("OK: PyMap3d eci2ecef vs. Matlab eci2ecef")
else:
    logging.error("eci2ecef did not match Matlab")

assert ecef_good and eci_good, "Matlab compare mismatch"
