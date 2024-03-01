import numpy as np
import pandas as pd
from numpy.linalg import lstsq, matrix_rank
from patsy.highlevel import ModelDesc, dmatrices
from patsy.missing import NAAction

from linearmodels.panel.covariance import HeteroskedasticCovariance, HomoskedasticCovariance, \
    OneWayClusteredCovariance
from linearmodels.panel.data import PanelData
from linearmodels.panel.results import PanelResults
from linearmodels.utility import AttrDict, MissingValueWarning, has_constant, \
    missing_value_warning_msg


class CovarianceManager(object):
    COVARIANCE_ESTIMATORS = {'unadjusted': HomoskedasticCovariance,
                             'homoskedastic': HomoskedasticCovariance,
                             'robust': HeteroskedasticCovariance,
                             'heteroskedastic': HeteroskedasticCovariance,
                             'oneway': OneWayClusteredCovariance,
                             'clustered': OneWayClusteredCovariance}

    def __init__(self, estimator, *cov_estimators):
        self._estimator = estimator
        self._supported = cov_estimators

    def __getitem__(self, item):
        if item not in self.COVARIANCE_ESTIMATORS:
            raise KeyError('Unknown covariance estimator type.')
        cov_est = self.COVARIANCE_ESTIMATORS[item]
        if cov_est not in self._supported:
            raise ValueError('Requested covariance estimator is not supported '
                             'for the {0}.'.format(self._estimator))
        return cov_est


class AbsorbingEffectError(Exception):
    pass


absorbing_error_msg = """
The model cannot be estimated. The included effects have fully absorbed
one or more of the variables. This occurs when one or more of the dependent
variable is perfectly explained using the effects included in the model.
"""


class AmbiguityError(Exception):
    pass


# TODO: 2 way cluster covariance
# TODO: Regression F-stat
# TODO: Pooled F-stat
# TODO: Verify alternative R2 definitions
# TODO: Bootstrap covariance
# TODO: Test covariance estimators vs IV versions
# TODO: Add likelihood and possibly AIC/BIC
# TODO: Correlation between FE and XB
# TODO: ??Alternative variance estimators??
# TODO: Documentation
# TODO: Example notebooks
# TODO: Test model residuals when compared to reference implementations
# TODO: Test other outputs


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
    other_effects : array-like, optional
        Category codes to use for any effects that are not entity or time
        effects. Each variable is treated as an effect.

    Notes
    -----
    The model is given by

    .. math::

        y_{it}=\alpha_i + \gamma_t +\beta^{\prime}x_{it}+\epsilon_{it}

    where :math:`\alpha_i` is omitted if ``entity_effect`` is ``False`` and
    :math:`\gamma_i` is omitted if ``time_effect`` is ``False``. If both ``entity_effect``  and
    ``time_effect`` are ``False``, the model reduces to :class:`PooledOLS`. If ``other_effects``
    is provided, then additional terms are present to reflect these effects.

    Model supports at most 2 effects.  These can be entity-time, entity-other, time-other or
    2 other.
    """

    def __init__(self, dependent, exog, *, weights=None, entity_effect=False, time_effect=False,
                 other_effects=None):
        self.dependent = PanelData(dependent, 'Dep')
        self.exog = PanelData(exog, 'Exog')
        self._entity_effect = entity_effect
        self._time_effect = time_effect
        self._constant = None
        self._formula = None
        self.weights = self._adapt_weights(weights)
        self._other_effect_cats = None
        self.other_effects = self._validate_effects(other_effects)
        self._validate_data()
        self._cov_estimators = CovarianceManager(self.__class__.__name__, HomoskedasticCovariance,
                                                 HeteroskedasticCovariance,
                                                 OneWayClusteredCovariance)

        self._name = self.__class__.__name__

    def _validate_effects(self, effects):
        if effects is None:
            return False
        effects = PanelData(effects, var_name='OtherEffect',
                            convert_dummies=False)
        num_effects = effects.nvar
        if num_effects + self.entity_effect + self.time_effect > 2:
            raise ValueError('At most two effects supported.')
        cats = {}
        effects_frame = effects.dataframe
        for col in effects_frame:
            cat = pd.Categorical(effects_frame[col])
            cats[col] = cat.codes.astype(np.int64)
        cats = pd.DataFrame(cats, index=effects_frame.index)
        cats = cats[effects_frame.columns]
        self._other_effect_cats = PanelData(cats)
        return True

    def _adapt_weights(self, weights):
        if weights is None:
            frame = self.dependent.dataframe.copy()
            frame.iloc[:, :] = 1
            frame.columns = ['weight']
            return PanelData(frame)

        frame = self.dependent.panel.iloc[0].copy()
        nobs, nentity = self.exog.nobs, self.exog.nentity

        if weights.ndim == 3 or weights.shape == (nobs, nentity):
            return PanelData(weights)

        weights = np.squeeze(weights)
        if weights.shape[0] == nobs and nobs == nentity:
            raise AmbiguityError('Unable to distinguish nobs form nentity since they are '
                                 'equal. You must use an 2-d array to avoid ambiguity.')
        if weights.shape[0] == nobs:
            weights = np.asarray(weights)[:, None]
            weights = weights @ np.ones((1, nentity))
            frame.iloc[:, :] = weights
        elif weights.shape[0] == nentity:
            weights = np.asarray(weights)[None, :]
            weights = np.ones((nobs, 1)) @ weights
            frame.iloc[:, :] = weights
        elif weights.shape[0] == nentity * nobs:
            frame = self.dependent.dataframe.copy()
            frame.iloc[:, :] = weights[:, None]
        else:
            raise ValueError('Weights do not have a supported shape.')
        return PanelData(frame)

    def _validate_data(self):
        y = self._y = self.dependent.values2d
        x = self._x = self.exog.values2d
        w = self._w = self.weights.values2d
        if y.shape[0] != x.shape[0]:
            raise ValueError('dependent and exog must have the same number of '
                             'observations.')
        if y.shape[0] != w.shape[0]:
            raise ValueError('weights must have the same number of '
                             'observations as dependent.')
        if self.other_effects:
            oe = self._other_effect_cats.dataframe
            if oe.shape[0] != y.shape[0]:
                raise ValueError('other_effects must have the same number of '
                                 'observations as dependent.')

        all_missing = np.any(np.isnan(y), axis=1) & np.all(np.isnan(x), axis=1)
        missing = (np.any(np.isnan(y), axis=1) |
                   np.any(np.isnan(x), axis=1) |
                   np.any(np.isnan(w), axis=1))
        if np.any(missing):
            if np.any(all_missing ^ missing):
                import warnings
                warnings.warn(missing_value_warning_msg, MissingValueWarning)
            self.dependent.drop(missing)
            self.exog.drop(missing)
            self.weights.drop(missing)
            if self.other_effects:
                self._other_effect_cats.drop(missing)
            x = self.exog.values2d

        w = self.weights.dataframe
        w = w / w.mean()
        self.weights = PanelData(w)

        if matrix_rank(x) < x.shape[1]:
            raise ValueError('exog does not have full column rank.')
        self._constant, self._constant_index = has_constant(x)

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

    @classmethod
    def from_formula(cls, formula, data, *, weights=None):
        na_action = NAAction(on_NA='raise', NA_types=[])
        data = PanelData(data)
        parts = formula.split('~')
        parts[1] = ' 0 + ' + parts[1]
        cln_formula = '~'.join(parts)

        mod_descr = ModelDesc.from_formula(cln_formula)
        rm_list = []
        effects = {'EntityEffect': False, 'FixedEffect': False, 'TimeEffect': False}
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
        mod = cls(dependent, exog, entity_effect=entity_effect,
                  time_effect=time_effect, weights=weights)
        mod.formula = formula
        return mod

    def _info(self):
        def stats(ids, name):
            bc = np.bincount(ids)
            index = ['mean', 'median', 'max', 'min', 'total']
            out = [bc.mean(), np.median(bc), bc.max(), bc.min(), bc.shape[0]]
            return pd.Series(out, index=index, name=name)

        entity_info = stats(self.dependent.entity_ids.squeeze(),
                            'Observations per entity')
        time_info = stats(self.dependent.time_ids.squeeze(),
                          'Observations per time period')
        other_info = None
        if self.other_effects:
            other_info = []
            oe = self._other_effect_cats.dataframe
            for c in oe:
                name = 'Observations per group (' + str(c) + ')'
                other_info.append(stats(oe[c].values.astype(np.int32), name))
            other_info = pd.DataFrame(other_info)

        return entity_info, time_info, other_info

    def _prepare_between(self):
        y = self.dependent.mean('entity', weights=self.weights).values
        x = self.exog.mean('entity', weights=self.weights).values
        # Weight transformation
        wcount, wmean = self.weights.count('entity'), self.weights.mean('entity')
        wsum = wcount * wmean
        w = wsum.values
        w = w / w.mean()

        return y, x, w

    def _rsquared(self, params, reweight=False):
        if self.has_constant and self.dependent.nvar == 1:
            # Constant only fast track
            return 0.0, 0.0, 0.0
        
        #############################################
        # R2 - Between
        #############################################
        y, x, w = self._prepare_between()
        if np.all(self.weights.values2d == 1.0) and not reweight:
            w = root_w = np.ones_like(w)
        else:
            root_w = np.sqrt(w)
        wx = root_w * x
        wy = root_w * y
        weps = wy - wx @ params
        residual_ss = float(weps.T @ weps)
        e = y
        if self.has_constant:
            e = y - (w * y).sum() / w.sum()

        total_ss = float(w.T @ (e ** 2))
        r2b = 1 - residual_ss / total_ss

        #############################################
        # R2 - Overall
        #############################################
        y = self.dependent.values2d
        x = self.exog.values2d
        w = self.weights.values2d
        root_w = np.sqrt(w)
        wx = root_w * x
        wy = root_w * y
        weps = wy - wx @ params
        residual_ss = float(weps.T @ weps)
        mu = (w * y).sum() / w.sum() if self.has_constant else 0
        we = wy - root_w * mu
        total_ss = float(we.T @ we)
        r2o = 1 - residual_ss / total_ss

        #############################################
        # R2 - Within
        #############################################
        # TODO: Test that this is correct in weighted and unweighted, const or not
        wy = self.dependent.demean('entity', weights=self.weights).values2d
        wx = self.exog.demean('entity', weights=self.weights).values2d
        weps = wy - wx @ params
        residual_ss = float(weps.T @ weps)
        total_ss = float(wy.T @ wy)
        if self.dependent.nobs == 1:
            r2w = 0
        else:
            r2w = 1 - residual_ss / total_ss

        return r2o, r2w, r2b

    def _postestimation(self, params, cov, debiased):
        r2o, r2w, r2b = self._rsquared(params)
        entity_info, time_info, other_info = self._info()
        res = AttrDict(params=params, deferred_cov=cov.deferred_cov,
                       debiased=debiased, name=self._name, var_names=self.exog.vars,
                       r2w=r2w, r2b=r2b, r2=r2w, r2o=r2o, s2=cov.s2,
                       entity_info=entity_info, time_info=time_info,
                       other_info=other_info, model=self,
                       cov_type='Unadjusted', index=self.dependent.dataframe.index)
        return res

    def _fit_lvsd(self, debiased=False):
        constant = self._constant
        has_effect = self.entity_effect or self.time_effect
        w = self.weights
        y = self.dependent
        x = self.exog
        # 1. Construct dummies
        # 2. Append to x
        # 3. Estimate parameters using x and y
        if self.entity_effect:
            d = ed = y.dummies('entity')
        if self.time_effect:
            d = td = y.dummies('time', drop_first=self.entity_effect)
        if self.entity_effect and self.time_effect:
            d = np.c_[ed, td]
        root_w = np.sqrt(w.values2d)
        wx = root_w * x.values2d
        if has_effect:
            wd = root_w * d
            if constant:
                wd -= root_w @ lstsq(root_w, wd)[0]
            wx = np.c_[wx, wd]
        wy = root_w * y.values2d
        params = lstsq(wx, wy)[0]
        return params

    @property
    def has_constant(self):
        return self._constant

    def _slow_path(self):
        """Frisch-Waigh-Lovell Implemtation, mostly for weighted"""
        has_effect = self.entity_effect or self.time_effect or self.other_effects
        w = self.weights.values2d
        root_w = np.sqrt(w)

        y = root_w * self.dependent.values2d
        x = root_w * self.exog.values2d
        if not has_effect:
            ybar = root_w @ lstsq(root_w, y)[0]
            return y, x, ybar, 0, 0

        drop_first = self._constant
        d = []
        if self.entity_effect:
            d.append(self.dependent.dummies('entity', drop_first=drop_first).values)
            drop_first = True
        if self.time_effect:
            d.append(self.dependent.dummies('time', drop_first=drop_first).values)
            drop_first = True
        if self.other_effects:
            oe = self._other_effect_cats.dataframe
            for c in oe:
                dummies = pd.get_dummies(oe[c], drop_first=drop_first).astype(np.float64)
                d.append(dummies.values)
                drop_first = True

        d = np.column_stack(d)
        if self.has_constant:
            d -= d.mean(0)

        wd = root_w * d
        x_mean = np.linalg.lstsq(wd, x)[0]
        y_mean = np.linalg.lstsq(wd, y)[0]

        # Save fitted unweighted effects to use in eps calculation
        x_effects = d @ x_mean
        y_effects = d @ y_mean

        # Purge fitted, weighted values
        x = x - wd @ x_mean
        y = y - wd @ y_mean

        ybar = root_w @ lstsq(root_w, y)[0]
        return y, x, ybar, y_effects, x_effects

    def _fast_path(self):
        has_effect = self.entity_effect or self.time_effect
        y = self.dependent.values2d
        x = self.exog.values2d
        ybar = y.mean(0)

        if not has_effect:
            return y, x, ybar

        y_gm = ybar
        x_gm = x.mean(0)

        y = self.dependent
        x = self.exog

        if self.entity_effect and self.time_effect:
            y = y.demean('both')
            x = x.demean('both')
        elif self.entity_effect:
            y = y.demean('entity')
            x = x.demean('entity')
        else:  # self.time_effect
            y = y.demean('time')
            x = x.demean('time')

        y = y.values2d
        x = x.values2d

        if self.has_constant:
            y = y + y_gm
            x = x + x_gm
        else:
            ybar = 0

        return y, x, ybar

    def fit(self, cov_type='unadjusted', debiased=False, **cov_config):

        unweighted = np.all(self.weights.values2d == 1.0)
        y_effects = x_effects = 0
        if unweighted and not self.other_effects:
            y, x, ybar = self._fast_path()
        else:
            y, x, ybar, y_effects, x_effects = self._slow_path()

        neffects = 0
        drop_first = self.has_constant
        if self.entity_effect:
            neffects += self.dependent.nentity - drop_first
            drop_first = True
        if self.time_effect:
            neffects += self.dependent.nobs - drop_first
            drop_first = True
        if self.other_effects:
            oe = self._other_effect_cats.dataframe
            for c in oe:
                neffects += oe[c].nunique() - drop_first
                drop_first = True

        if self.entity_effect or self.time_effect or self.other_effects:
            if matrix_rank(x) < x.shape[1]:
                raise AbsorbingEffectError(absorbing_error_msg)

        params = np.linalg.lstsq(x, y)[0]

        df_model = x.shape[1] + neffects
        df_resid = y.shape[0] - df_model
        cov_denom = df_resid if debiased else y.shape[0]
        # TODO: Clustered covariance needs work
        cov_est = self._cov_estimators[cov_type]
        cov = cov_est(y, x, params, cov_denom, **cov_config)
        weps = y - x @ params
        eps = weps
        if not unweighted:
            _y = self.dependent.values2d
            _x = self.exog.values2d
            eps = _y - y_effects - (_x - x_effects) @ params
        resid_ss = float(weps.T @ weps)

        if self.has_constant:
            mu = ybar
        else:
            mu = 0
        total_ss = float((y - mu).T @ (y - mu))
        res = self._postestimation(params, cov, debiased)
        r2 = 1 - resid_ss / total_ss
        res.update(dict(df_resid=df_resid, df_model=df_model, nobs=y.shape[0],
                        residual_ss=resid_ss, total_ss=total_ss, wresid=weps, resid=eps,
                        r2=r2))
        return PanelResults(res)


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
        self._cov_estimators = CovarianceManager(self.__class__.__name__, HomoskedasticCovariance,
                                                 HeteroskedasticCovariance,
                                                 OneWayClusteredCovariance)

    @classmethod
    def from_formula(cls, formula, data, *, weights=None):
        na_action = NAAction(on_NA='raise', NA_types=[])
        data = PanelData(data)
        parts = formula.split('~')
        parts[1] = ' 0 + ' + parts[1]
        cln_formula = '~'.join(parts)
        dependent, exog = dmatrices(cln_formula, data.dataframe,
                                    return_type='dataframe', NA_action=na_action)
        mod = cls(dependent, exog, weights=weights)
        mod.formula = formula
        return mod

    def fit(self, cov_type='unadjusted', debiased=False, **cov_config):
        y = self.dependent.values2d
        x = self.exog.values2d
        w = self.weights.values2d
        root_w = np.sqrt(w)
        wx = root_w * x
        wy = root_w * y

        params = lstsq(wx, wy)[0]

        nobs = y.shape[0]
        df_model = x.shape[1]
        df_resid = nobs - df_model
        cov_denom = nobs if not debiased else df_resid
        cov_est = self._cov_estimators[cov_type]
        cov = cov_est(wy, wx, params, cov_denom, **cov_config)
        weps = wy - wx @ params
        eps = y - x @ params
        residual_ss = float(weps.T @ weps)
        e = y
        if self._constant:
            e = e - (w * y).sum() / w.sum()

        total_ss = float(w.T @ (e ** 2))
        r2 = 1 - residual_ss / total_ss

        res = self._postestimation(params, cov, debiased)
        res.update(dict(df_resid=df_resid, df_model=df_model, nobs=y.shape[0],
                        residual_ss=residual_ss, total_ss=total_ss, r2=r2, wresid=weps,
                        resid=eps, index=self.dependent.dataframe.index))
        return PanelResults(res)


class BetweenOLS(PooledOLS):
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
        self._cov_estimators = CovarianceManager(self.__class__.__name__, HomoskedasticCovariance,
                                                 HeteroskedasticCovariance)

    def fit(self, reweight=False, cov_type='unadjusted', debiased=False, **cov_config):
        """
        Estimate model parameters

        Parameters
        ----------
        reweight : bool
            Flag indicating to reweight observations if the input data is
            unbalanced
        cov_type : str
            Either 'unadjusted' for homoskedastic covariance or 'robust' for
            heteroskedasticity robust covariance estimation.
        debiased : bool
            Flag indicating to use a debiased parameter covariance estimator

        Returns
        -------
        results : PanelResults
            Estimation results
        """
        y, x, w = self._prepare_between()
        if np.all(self.weights.values2d == 1.0) and not reweight:
            w = root_w = np.ones_like(w)
        else:
            root_w = np.sqrt(w)

        wx = root_w * x
        wy = root_w * y
        params = lstsq(wx, wy)[0]

        df_resid = y.shape[0] - x.shape[1]
        df_model = x.shape[1],
        nobs = y.shape[0]
        cov_denom = y.shape[0] if not debiased else df_resid
        cov_est = self._cov_estimators[cov_type]
        cov = cov_est(wy, wx, params, cov_denom, **cov_config)
        weps = wy - wx @ params
        eps = y - x @ params
        residual_ss = float(weps.T @ weps)
        e = y
        if self._constant:
            e = y - (w * y).sum() / w.sum()

        total_ss = float(w.T @ (e ** 2))
        r2 = 1 - residual_ss / total_ss

        res = self._postestimation(params, cov, debiased)
        res.update(dict(df_resid=df_resid, df_model=df_model, nobs=nobs,
                        residual_ss=residual_ss, total_ss=total_ss, r2=r2, wresid=weps, resid=eps,
                        index=self.dependent.entities))

        return PanelResults(res)

    @classmethod
    def from_formula(cls, formula, data, *, weights=None):
        return super(BetweenOLS, cls).from_formula(formula, data, weights=weights)


class FirstDifferenceOLS(PooledOLS):
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
        if self._constant:
            raise ValueError('Constants are not allowed in first difference regressions.')
        if self.dependent.nobs < 2:
            raise ValueError('Panel must have at least 2 time periods')
        self._cov_estimators = CovarianceManager(self.__class__.__name__, HomoskedasticCovariance,
                                                 HeteroskedasticCovariance)

    def fit(self, cov_type='unadjusted', debiased=False, **cov_config):
        y = self.dependent.first_difference().values2d
        x = self.exog.first_difference().values2d

        w = 1.0 / self.weights.panel.values
        w = w[:, :-1] + w[:, 1:]
        w = 1.0 / w
        w = pd.Panel(w, items=self.weights.panel.items,
                     major_axis=self.weights.panel.major_axis[1:],
                     minor_axis=self.weights.panel.minor_axis)
        w = w.swapaxes(1, 2).to_frame(filter_observations=False)
        w = w.reindex(self.weights.dataframe.index).dropna(how='any')
        index = w.index
        w = w.values

        w /= w.mean()
        root_w = np.sqrt(w)

        wx = root_w * x
        wy = root_w * y
        params = lstsq(wx, wy)[0]
        df_resid = y.shape[0] - x.shape[1]
        cov_denom = df_resid if debiased else y.shape[0]
        cov_est = self._cov_estimators[cov_type]
        cov = cov_est(wy, wx, params, cov_denom, **cov_config)

        weps = wy - wx @ params
        eps = y - x @ params
        residual_ss = float(weps.T @ weps)
        total_ss = float(w.T @ (y ** 2))
        r2 = 1 - residual_ss / total_ss

        res = self._postestimation(params, cov, debiased)
        res.update(dict(df_resid=df_resid, df_model=x.shape[1], nobs=y.shape[0],
                        residual_ss=residual_ss, total_ss=total_ss, r2=r2,
                        resid=eps, wresid=weps, index=index))

        return PanelResults(res)

    @classmethod
    def from_formula(cls, formula, data, *, weights=None):
        return super(FirstDifferenceOLS, cls).from_formula(formula, data, weights=weights)
