#!/usr/bin/env python
"""
Example Kitt Peak

./demo_azel2radec.py 264.91833333333335 37.91138888888889 31.9583 -111.5967 2014-12-25T22:00:00MST
"""
from pymap3d import azel2radec

if __name__ == "__main__":  # pragma: no cover
    from argparse import ArgumentParser

    p = ArgumentParser(description="convert azimuth and elevation to "
                       "right ascension and declination")
    p.add_argument('azimuth', help='azimuth [deg]', type=float)
    p.add_argument('elevation', help='elevation [deg]', type=float)
    p.add_argument('lat', help='WGS84 obs. lat [deg]', type=float)
    p.add_argument('lon', help='WGS84 obs. lon [deg]',type=float)
    p.add_argument('time', help='obs. time YYYY-mm-ddTHH:MM:SSZ')
    p = p.parse_args()

    ra, dec = azel2radec(p.azimuth, p.elevation, p.lat, p.lon, p.time)

    print('ra [deg] {} , dec [deg] = {}'.format(ra, dec))
