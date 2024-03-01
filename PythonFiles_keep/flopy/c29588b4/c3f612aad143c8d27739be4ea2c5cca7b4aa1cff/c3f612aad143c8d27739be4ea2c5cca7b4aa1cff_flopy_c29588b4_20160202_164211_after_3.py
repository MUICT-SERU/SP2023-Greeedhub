import sys
import numpy as np


class HydmodBinaryData(object):
    """
    The HydmodBinaryData class is a class to that defines the data types for
    integer, floating point, and character data in HYDMOD binary
    files. The HydmodBinaryData class is the super class from which the
    specific derived class HydmodObs is formed.  This class should not be
    instantiated directly.

    """

    def __init__(self):

        self.integer = np.int32
        self.integerbyte = self.integer(1).nbytes

        self.character = np.uint8
        self.textbyte = 1

        return

    def set_float(self, precision):
        self.precision = precision
        if precision.lower() == 'double':
            self.real = np.float64
            self.floattype = 'f8'
        else:
            self.real = np.float32
            self.floattype = 'f4'
        self.realbyte = self.real(1).nbytes
        return

    def read_hyd_text(self, nchar=20):
        textvalue = self._read_values(self.character, nchar).tostring()
        if not isinstance(textvalue, str):
            textvalue = textvalue.decode().strip()
        else:
            textvalue = textvalue.strip()
        return textvalue

    def read_integer(self):
        return self._read_values(self.integer, 1)[0]

    def read_real(self):
        return self._read_values(self.real, 1)[0]

    def read_record(self, count):
        return self._read_values(self.dtype, count)

    def _read_values(self, dtype, count):
        return np.fromfile(self.file, dtype, count)


class HydmodObs(HydmodBinaryData):
    """
    HydmodObs Class - used to read binary MODFLOW HYDMOD package output

    Parameters
    ----------
    filename : str
        Name of the hydmod output file
    verbose : boolean
        If true, print additional information to to the screen during the
        extraction.  (default is False)
    hydlbl_len : int
        Length of hydmod labels. (default is 20)

    Returns
    -------
    None

    """

    def __init__(self, filename, verbose=False, hydlbl_len=20):
        """
        Class constructor.

        """
        super(HydmodObs, self).__init__()
        # initialize class information
        self.verbose = verbose
        # --open binary head file
        self.file = open(filename, 'rb')
        # NHYDTOT,ITMUNI
        self.nhydtot = self.read_integer()
        precision = 'single'
        if self.nhydtot < 0:
            self.nhydtot = abs(self.nhydtot)
            precision = 'double'
        self.set_float(precision)

        # continue reading the file
        self.itmuni = self.read_integer()
        self.v = np.empty(self.nhydtot, dtype=np.float)
        self.v.fill(1.0E+32)
        ctime = self.read_hyd_text(nchar=4)
        self.hydlbl_len = int(hydlbl_len)
        # read HYDLBL
        hydlbl = []
        for idx in range(0, self.nhydtot):
            cid = self.read_hyd_text(self.hydlbl_len)
            hydlbl.append(cid)
        self.hydlbl = np.array(hydlbl)

        # create dtype
        dtype = [('totim', self.floattype)]
        for site in self.hydlbl:
            if not isinstance(site, str):
                site_name = site.decode().strip()
            else:
                site_name = site.strip()
            dtype.append((site_name, self.floattype))
        self.dtype = np.dtype(dtype)

        self.data = None
        self._read_data()

    def get_times(self):
        """
        Get a list of unique times in the file

        Returns
        ----------
        out : list of floats
            List contains unique simulation times (totim) in binary file.

        """
        return self.data['totim'].reshape(self.get_ntimes()).tolist()

    def get_ntimes(self):
        """
        Get the number of times in the file

        Returns
        ----------
        out : int
            The number of simulation times (totim) in binary file.

        """
        return self.data['totim'].shape[0]

    def get_nobs(self):
        """
        Get the number of observations in the file

        Returns
        ----------
        out : tuple of int
            A tupe with the number of records and number of flow items
            in the file. The number of flow items is non-zero only if
            swrtype='flow'.

        """
        return self.nhydtot

    def get_obsnames(self):
        """
        Get a list of observation names in the file

        Returns
        ----------
        out : list of strings
            List of observation names in the binary file. totim is not
            included in the list of observation names.

        """
        return list(self.data.dtype.names[1:])

    def get_data(self, idx=None, obsname=None, totim=None):
        """
        Get data from the observation file.

        Parameters
        ----------
        idx : int
            The zero-based record number.  The first record is record 0.
            If idx is None and totim are None, data for all simulation times
            are returned. (default is None)
        obsname : string
            The name of the observation to return. If obsname is None, all
            observation data are returned. (default is None)
        totim : float
            The simulation time to return. If idx is None and totim are None,
            data for all simulation times are returned. (default is None)

        Returns
        ----------
        data : numpy record array
            Array has size (ntimes, nitems). totim is always returned. nitems
            is 2 if idx or obsname is not None or nobs+1.

        See Also
        --------

        Notes
        -----
        If both idx and obsname are None, will return all of the observation
        data.

        Examples
        --------
        >>> hyd = HydmodObs("my_model.hyd")
        >>> ts = hyd.get_data()

        """
        i0 = 0
        i1 = self.data.shape[0]
        if totim is not None:
            idx = np.where(self.data['totim'] == totim)[0][0]
            i0 = idx
            i1 = idx + 1
        elif idx is not None:
            if idx < i1:
                i0 = idx
            i1 = i0 + 1
        r = None
        if obsname is None:
            obsname = self.get_obsnames()
        else:
            if obsname is not None:
                if obsname not in self.data.dtype.names:
                    obsname = None
                else:
                    if not isinstance(obsname, list):
                        obsname = [obsname]
        if obsname is not None:
            obsname.insert(0, 'totim')
            r = self._get_selection(obsname)[i0:i1]
        return r


    def get_dataframe(self, start_datetime='1-1-1970',
                      idx=None, obsname=None, totim=None, timeunit='D'):
        """
        Get pandas dataframe with the incremental and cumulative water budget
        items in the hydmod file.

        Parameters
        ----------
        start_datetime : str
            If start_datetime is passed as None, the rows are indexed on totim.
            Otherwise, a DatetimeIndex is set. (default is 1-1-1970).
        idx : int
            The zero-based record number.  The first record is record 0.
            If idx is None and totim are None, a dataframe with all simulation
            times is  returned. (default is None)
        obsname : string
            The name of the observation to return. If obsname is None, all
            observation data are returned. (default is None)
        totim : float
            The simulation time to return. If idx is None and totim are None,
            a dataframe with all simulation times is returned.
            (default is None)
        timeunit : string
            time unit of the simulation time. Valid values are 'S'econds,
            'M'inutes, 'H'ours, 'D'ays, 'Y'ears. (default is 'D').

        Returns
        -------
        out : pandas dataframe
            Pandas dataframe of selected data.

        See Also
        --------

        Notes
        -----
        If both idx and obsname are None, will return all of the observation
        data as a dataframe.

        Examples
        --------
        >>> hyd = HydmodObs("my_model.hyd")
        >>> df = hyd.get_dataframes()

        """

        try:
            import pandas as pd
            from ..utils.utils_def import totim_to_datetime
        except Exception as e:
            raise Exception(
                    "HydmodObs.get_dataframe() error import pandas: " + \
                    str(e))
        i0 = 0
        i1 = self.data.shape[0]
        if totim is not None:
            idx = np.where(self.data['totim'] == totim)[0][0]
            i0 = idx
            i1 = idx + 1
        elif idx is not None:
            if idx < i1:
                i0 = idx
            i1 = i0 + 1

        if obsname is None:
            obsname = self.get_obsnames()
        else:
            if obsname is not None:
                if obsname not in self.data.dtype.names:
                    obsname = None
                else:
                    if not isinstance(obsname, list):
                        obsname = [obsname]
        if obsname is None:
            return None

        obsname.insert(0, 'totim')

        dti = self.get_times()[i0:i1]
        if start_datetime is not None:
            dti = totim_to_datetime(dti,
                                    start=pd.to_datetime(start_datetime),
                                    timeunit=timeunit)

        df = pd.DataFrame(self.data[i0:i1], index=dti, columns=obsname)
        return df

    def _read_data(self):

        if self.data is not None:
            return

        while True:
            try:
                r = self.read_record(count=1)
                if self.data is None:
                    self.data = r.copy()
                elif r.size == 0:
                    break
                else:
                    # should be hstack based on (https://mail.scipy.org/pipermail/numpy-discussion/2010-June/051107.html)
                    self.data = np.hstack((self.data, r))
            except:
                break
        return

    def _get_selection(self, names):
        if not isinstance(names, list):
            names = [names]
        dtype2 = np.dtype(
                {name: self.data.dtype.fields[name] for name in names})
        return np.ndarray(self.data.shape, dtype2, self.data, 0,
                          self.data.strides)
