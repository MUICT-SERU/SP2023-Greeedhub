import numpy as np
import pandas as pd
import xarray as xr

dim_err = '{0} has too many dims.  Maximum is 2, actual is {2}'
type_err = 'Only ndarrays, DataArrays and Series and DataFrames are permitted'


def convert_columns(s):
    if pd.api.types.is_categorical(s):
        out = pd.get_dummies(s, drop_first=True)
        out.columns = [s.name + '.' + c for c in out]
        return out
    return s


def expand_categoricals(x):
    if isinstance(x, pd.Series):
        return convert_columns(x)
    if isinstance(x, pd.DataFrame):
        return pd.concat([convert_columns(x[c]) for c in x.columns], axis=1)
    elif isinstance(x, pd.Panel):
        raise NotImplementedError


class DataHandler(object):
    def __init__(self, x, var_name='x'):

        if isinstance(x, DataHandler):
            x = x.original

        self.original = x
        xndim = x.ndim
        if xndim > 2:
            raise ValueError(dim_err.format(var_name, xndim))

        if isinstance(x, np.ndarray):
            x = x.view()
            if xndim == 1:
                x.shape = (x.shape[0], -1)

            self._ndarray = x
            index = list(range(x.shape[0]))
            cols = [var_name + '.{0}'.format(i) for i in range(x.shape[1])]
            self._pandas = pd.DataFrame(x, index=index, columns=cols)
            self._labels = {0: index,
                            1: cols}

        elif isinstance(x, (pd.Series, pd.DataFrame)):
            dts = [x.dtype] if xndim == 1 else x.dtypes
            for dt in dts:
                if not (pd.api.types.is_numeric_dtype(dt)
                        or pd.api.types.is_categorical_dtype(dt)):
                    raise ValueError('Only numeric or categorical data permitted')

            x = expand_categoricals(x)
            if x.ndim == 1:
                x = pd.DataFrame({var_name: x})

            self._pandas = x
            self._ndarray = self._pandas.values
            self._labels = {i: list(label) for i, label in zip(range(x.ndim), x.axes)}

        elif isinstance(x, xr.DataArray):
            raise NotImplementedError('Not implemented yet.')
        else:
            raise TypeError(type_err)

    @property
    def pandas(self):
        return self._pandas

    @property
    def ndarray(self):
        return self._ndarray

    @property
    def shape(self):
        return self._ndarray.shape

    @property
    def ndim(self):
        return self._ndarray.ndim

    @property
    def cols(self):
        return self._labels[1]

    @property
    def rows(self):
        return self._labels[0]

    @property
    def labels(self):
        return self._labels
