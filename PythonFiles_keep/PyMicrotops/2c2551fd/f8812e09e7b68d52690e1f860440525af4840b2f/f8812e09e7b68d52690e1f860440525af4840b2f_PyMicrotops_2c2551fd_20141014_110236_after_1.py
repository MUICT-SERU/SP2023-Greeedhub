import numpy as np
import pandas as pd
from dateutil.parser import parse
from read_from_serial import read_serial_data

class Microtops:
    """Loads and processes a data file from the Microtops handheld sun photometer.
    Allows easy plotting, and estimation of AOT at an arbitrary wavelength through
    interpolation with the Angstrom exponent

    File should be in CSV format, as produced by the instrument.

    This module requires:
    * numpy
    * pandas
    * dateutil
    """

    def __init__(self, filename):
        self.filename = filename
        self._load_file(filename)

    @classmethod
    def read_from_serial(self, port, filename, **kwargs):
        read_serial_data(port, filename, **kwargs)
        return Microtops(filename)

    def _load_file(self, filename):
        self.data = pd.read_csv(filename)

        def f(s):
            return parse(s['DATE'] + " " + s['TIME'])

        self.data.index = pd.DatetimeIndex(self.data.apply(f, axis=1))

        self._process_wavelengths()

    def plot(self, wavelengths=None, start_time=None, end_time=None, **kwargs):
        data = self.data[start_time:end_time]

        if wavelengths is None:
            wavelengths = self.wavelengths

        col_names = map(lambda x: 'AOT%d' % (int(x)), wavelengths)

        print col_names
        data.ix[:, col_names].plot(**kwargs)

    def _process_wavelengths(self):
        """
        Extract wavelengths from the column headers
        """
        aot_cols = [c for c in self.data.columns if 'AOT' in c]
        wvs = map(lambda x: int(x.replace('AOT', '')), aot_cols)

        self.wavelengths = wvs

    def aot(self, wavelength, start_time=None, end_time=None):
        data = self.data[start_time:end_time]

        wavelength = int(wavelength)

        if wavelength in self.wavelengths:
            # This wavelength was measured by the Microtops,
            # so just return it
            return data['AOT%d' % wavelength]
        else:
            # Need to interpolate using Angstrom exp

            # First we choose the two closest wavelengths
            wvs = np.array(self.wavelengths)
            diff = wavelength - wvs
            wv_below = wvs[np.argmin(diff[diff > 0])]
            wv_above = wvs[np.argmin(diff[diff < 0])]

            aot_below = data["AOT%d" % wv_below]
            aot_above = data["AOT%d" % wv_above]

            # Then we calculate the Angstrom exp for every observation
            angstrom = -1 * (np.log(aot_below / aot_above) / (np.log(float(wv_below) / wv_above)))

            # Then we use the exponent to interpolate
            result = aot_below * ((float(wavelength) / wv_below)**(-1*angstrom))

            return result