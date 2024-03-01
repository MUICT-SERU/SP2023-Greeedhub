import numpy as np
import pandas as pd
from numpy.linalg import matrix_rank, pinv
from patsy.highlevel import dmatrices, ModelDesc
from patsy.missing import NAAction


from linearmodels.panel.data import PanelData
from linearmodels.utility import has_constant

class AmbiguityError(Exception):
    pass

class PanelOLS(object):
    r"""
    Parameters
    ----------
    dependent: array-like
        Dependent (left-hand-side) variable (time by entity)
    exog: array-like
        Exogenous or right-hand-side variables (variable by time by entity). 
    entity_effect : bool, optional
        Flag whether to include entity (fixed) effects in the model
    time_effect : bool, optional
        Flag whether to include time effects in the model

    Notes
    -----
    The model is given by

    .. math::

        y_{it}=\alpha_i + \gamma_t +\beta^{\prime}x_{it}+\epsilon_{it}

    where :math:`\alpha_i` is omitted if ``entity_effect`` is ``False`` and
    :math:`\gamma_i` is omitted if ``time_effect`` is ``False``. If both ``entity_effect``  and
    ``time_effect`` are ``False``, the model reduces to :class:`PooledOLS`.
    """

    def __init__(self, dependent, exog, *, weights=None, entity_effect=False, time_effect=False):
        self.dependent = PanelData(dependent, 'dependent')
        self.exog = PanelData(exog, 'exog')
        self._constant = None
        self._formula = None
        self.weights = self._adapt_weights(weights)
        self._validate_data()
        # Normalize weights
        avg_w = np.nanmean(self.weights.dataframe.values)
        self.weights = PanelData(self.weights.dataframe / avg_w)
        self._entity_effect = entity_effect
        self._time_effect = time_effect

    def _adapt_weights(self, weights):
        frame = self.dependent.panel.iloc[0].copy()
        nobs, nentity = self.exog.nobs, self.exog.nentity
        if weights is None:
            frame.iloc[:, :] = 1
            frame = frame.T.stack(dropna=False)
            frame.name = 'weight'
            return PanelData(pd.DataFrame(frame))

        if np.asarray(weights).squeeze().ndim == 1:
            if weights.shape[0] == nobs and nobs == nentity:
                raise AmbiguityError('Unable to distinguish nobs form nentity since they are '
                                     'equal. You must use an 2-d array to avoid ambiguity.')
            if weights.shape[0] == nobs:
                weights = np.asarray(weights).squeeze()[:, None]
                weights = weights @ np.ones((1, nentity))
                frame.iloc[:, :] = weights
            elif weights.shape[0] == nentity:
                weights = np.asarray(weights).squeeze()[None, :]
                weights = np.ones((nobs, 1)) @ weights
                frame.iloc[:, :] = weights
            elif weights.shape[0] == nentity * nobs:
                frame = self.dependent.dataframe.copy()
                frame.iloc[:, :] = weights[:, None]
            else:
                raise ValueError('Weights do not have a supported shape.')
            return PanelData(frame)

        return PanelData(weights)

    def _validate_data(self):
        y = self._y = self.dependent.a2d
        x = self._x = self.exog.a2d
        w = self._w = self.weights.a2d
        if y.shape[0] != x.shape[0]:
            raise ValueError('dependent and exog must have the same number of '
                             'observations.')
        if y.shape[0] != w.shape[0]:
            raise ValueError('weights must have the same number of observations as dependent.')

        all_missing = np.any(np.isnan(y), axis=1) & np.all(np.isnan(x), axis=1)
        missing = (np.any(np.isnan(y), axis=1) |
                   np.any(np.isnan(x), axis=1) |
                   np.any(np.isnan(w), axis=1))
        if np.any(missing):
            if np.any(all_missing ^ missing):
                import warnings
                warnings.warn('Missing values detected. Dropping rows with one '
                              'or more missing observation.', UserWarning)
            self.dependent.drop(missing)
            self.exog.drop(missing)
            self.weights.drop(missing)
            x = self.exog.a2d

        self._constant, self._constant_index = has_constant(x)
        if matrix_rank(x) < x.shape[1]:
            raise ValueError('exog does not have full column rank.')

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, value):
        self._formula = value

    @property
    def entity_effect(self):
        return self._entity_effect

    @property
    def time_effect(self):
        return self._time_effect

    @staticmethod
    def from_formula(formula, data):
        na_action = NAAction(on_NA='raise', NA_types=[])
        data = PanelData(data)
        cln_formula = formula + ' + 0 '
        mod_descr = ModelDesc.from_formula(cln_formula)
        rm_list = []
        effects = {'EntityEffect':False, 'FixedEffect':False, 'TimeEffect':False}
        for term in mod_descr.rhs_termlist:
            if term.name() in effects:
                effects[term.name()] = True
                rm_list.append(term)
        for term in rm_list:
            mod_descr.rhs_termlist.remove(term)

        if effects['EntityEffect'] and effects['FixedEffect']:
            raise ValueError('Cannot use both FixedEffect and EntityEffect')
        entity_effect = effects['EntityEffect'] or effects['FixedEffect']
        time_effect = effects['TimeEffect']
        dependent, exog = dmatrices(mod_descr, data.dataframe,
                                    return_type='dataframe', NA_action=na_action)
        mod = PanelOLS(dependent, exog, entity_effect=entity_effect, time_effect=time_effect)
        mod.formula = formula
        return mod

    def fit(self):
        y = self.dependent
        x = self.exog
        if self._constant:
            const_name = x.dataframe.columns[self._constant_index]
            const_col = x.dataframe[const_name]
        if self.entity_effect and self.time_effect:
            y = y.demean('both')
            x = x.demean('both')
        elif self.entity_effect:
            y = y.demean('entity')
            x = x.demean('entity')
        elif self.time_effect:
            y = y.demean('time')
            x = x.demean('time')
        if self._constant:
            x.dataframe.loc[:,const_name] = const_col
        y = y.a2d
        x = x.a2d

        return pinv(x) @ y


class PooledOLS(PanelOLS):
    r"""
    Estimation of linear model with pooled parameters

    Parameters
    ----------
    dependent: array-like
        Dependent (left-hand-side) variable (time by entity)
    exog: array-like
        Exogenous or right-hand-side variables (variable by time by entity). 

    Notes
    -----
    The model is given by

    .. math::

        y_{it}=\beta^{\prime}x_{it}+\epsilon_{it}
    """

    def __init__(self, dependent, exog, *, weights=None):
        super(PooledOLS, self).__init__(dependent, exog, weights=weights)

    @staticmethod
    def from_formula(formula, data):
        na_action = NAAction(on_NA='raise', NA_types=[])
        data = PanelData(data)
        parts = formula.split('~')
        parts[1] = ' 0 + ' + parts[1]
        cln_formula = '~'.join(parts)
        dependent, exog = dmatrices(cln_formula, data.dataframe,
                                    return_type='dataframe', NA_action=na_action)
        mod = PooledOLS(dependent, exog)
        mod.formula = formula
        return mod

    def fit(self):
        y = self.dependent.a2d
        x = self.exog.a2d
        return pinv(x) @ y


class BetweenOLS(PanelOLS):
    r"""
    Parameters
    ----------
    dependent: array-like
        Dependent (left-hand-side) variable (time by entity)
    exog: array-like
        Exogenous or right-hand-side variables (variable by time by entity). 

    Notes
    -----
    The model is given by

    .. math::

        \bar{y}_{i}=  \beta^{\prime}\bar{x}_{i}+\bar{\epsilon}_{i}

    where :math:`\bar{z}` is the time-average.
    """

    def __init__(self, dependent, exog, *, weights=None):
        super(BetweenOLS, self).__init__(dependent, exog, weights=weights)

    def fit(self):
        y = self.dependent.mean('time').values
        x = self.exog.mean('time').values

        return pinv(x) @ y


class FirstDifferenceOLS(PanelOLS):
    r"""
    Parameters
    ----------
    dependent: array-like
        Dependent (left-hand-side) variable (time by entity)
    exog: array-like
        Exogenous or right-hand-side variables (variable by time by entity). 

    Notes
    -----
    The model is given by

    .. math::

        \Delta y_{it}=\beta^{\prime}\Delta x_{it}+\Delta\epsilon_{it}
    """

    def __init__(self, dependent, exog, *, weights=None):
        super(FirstDifferenceOLS, self).__init__(dependent, exog, weights=weights)

    def fit(self):
        y = self.dependent.first_difference().a2d
        x = self.exog.first_difference().a2d

        return pinv(x) @ y
