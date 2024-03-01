import warnings

import numpy as np
import pandas as pd
import pytest
from numpy.linalg import pinv
from numpy.testing import assert_allclose
from statsmodels.api import add_constant

from linearmodels.iv import IV2SLS, IVLIML, IVGMM, IVGMMCUE
from linearmodels.iv.model import _OLS
from linearmodels.utility import AttrDict


@pytest.fixture(scope='module')
def data():
    n, q, k, p = 1000, 2, 5, 3
    np.random.seed(12345)
    clusters = np.random.randint(0, 10, n)
    rho = 0.5
    r = np.zeros((k + p + 1, k + p + 1))
    r.fill(rho)
    r[-1, 2:] = 0
    r[2:, -1] = 0
    r[-1, -1] = 0.5
    r += np.eye(9) * 0.5
    v = np.random.multivariate_normal(np.zeros(r.shape[0]), r, n)
    x = v[:, :k]
    z = v[:, k:k + p]
    e = v[:, [-1]]
    params = np.arange(1, k + 1) / k
    params = params[:, None]
    y = x @ params + e
    xhat = z @ np.linalg.pinv(z) @ x
    nobs, nvar = x.shape
    s2 = e.T @ e / nobs
    s2_debiased = e.T @ e / (nobs - nvar)
    v = xhat.T @ xhat / nobs
    vinv = np.linalg.inv(v)
    kappa = 0.99
    vk = (x.T @ x * (1 - kappa) + kappa * xhat.T @ xhat) / nobs
    return AttrDict(nobs=nobs, e=e, x=x, y=y, z=z, xhat=xhat,
                    params=params, s2=s2, s2_debiased=s2_debiased,
                    clusters=clusters, nvar=nvar, v=v, vinv=vinv, vk=vk,
                    kappa=kappa, dep=y, exog=x[:, q:], endog=x[:, :q],
                    instr=z)


def get_all(v):
    attr = [d for d in dir(v) if not d.startswith('_')]
    for a in attr:
        val = getattr(v, a)
        if a in ('conf_int', 'durbin', 'wu_hausman', 'c_stat'):
            val = val()


class TestErrors(object):
    def test_rank_deficient_exog(self, data):
        exog = data.exog.copy()
        exog[:, :2] = 1
        with pytest.raises(ValueError):
            IV2SLS(data.dep, exog, data.endog, data.instr)

    def test_rank_deficient_endog(self, data):
        endog = data.endog.copy()
        endog[:, :2] = 1
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, endog, data.instr)
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, data.exog, data.instr)

    def test_rank_deficient_instr(self, data):
        instr = data.instr.copy()
        instr[:, :2] = 1
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, data.endog, instr)
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, data.endog, data.exog)

    def test_kappa_error(self, data):
        with pytest.raises(ValueError):
            IVLIML(data.dep, data.exog, data.endog, data.instr, kappa=np.array([1]))

    def test_fuller_error(self, data):
        with pytest.raises(ValueError):
            IVLIML(data.dep, data.exog, data.endog, data.instr, fuller=np.array([1]))

    def test_kappa_fuller_warning(self, data):
        with warnings.catch_warnings(record=True) as w:
            IVLIML(data.dep, data.exog, data.endog, data.instr, kappa=0.99, fuller=1)
        assert len(w) == 1

    def test_invalid_cat(self, data):
        instr = data.instr.copy()
        n = data.instr.shape[0]
        cat = pd.Series(['a'] * (n // 2) + ['b'] * (n // 2))
        instr = pd.DataFrame(instr)
        instr['cat'] = cat
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, data.endog, instr)

    def test_no_regressors(self, data):
        with pytest.raises(ValueError):
            IV2SLS(data.dep, None, None, None)

    def test_too_few_instruments(self, data):
        with pytest.raises(ValueError):
            IV2SLS(data.dep, data.exog, data.endog, None)


def test_2sls_direct(data):
    mod = IV2SLS(data.dep, add_constant(data.exog), data.endog, data.instr)
    res = mod.fit()
    x = np.c_[add_constant(data.exog), data.endog]
    z = np.c_[add_constant(data.exog), data.instr]
    y = data.y
    xhat = z @ pinv(z) @ x
    params = pinv(xhat) @ y
    assert_allclose(res.params, params.ravel())
    # This is just a quick smoke check of results
    get_all(res)


def test_2sls_direct_small(data):
    mod = IV2SLS(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit()
    res2 = mod.fit(debiased=True)
    assert np.all(res.tstats != res2.tstats)
    get_all(res2)
    fs = res.first_stage
    stats = fs.diagnostics
    # Fetch again to test cache
    get_all(res2)


def test_liml_direct(data):
    mod = IVLIML(data.dep, data.exog, data.endog, data.instr)
    nobs = data.dep.shape[0]
    ninstr = data.exog.shape[1] + data.instr.shape[1]
    res = mod.fit()
    get_all(res)
    mod2 = IVLIML(data.dep, data.exog, data.endog, data.instr, kappa=res.kappa)
    res2 = mod2.fit()
    assert_allclose(res.params, res2.params)
    mod3 = IVLIML(data.dep, data.exog, data.endog, data.instr, fuller=1)
    res3 = mod3.fit()
    assert_allclose(res3.kappa, res.kappa - 1 / (nobs - ninstr))


def test_2sls_ols_equiv(data):
    mod = IV2SLS(data.dep, data.exog, None, None)
    res = mod.fit()
    params = pinv(data.exog) @ data.dep
    assert_allclose(res.params, params.ravel())


def test_gmm_iter(data):
    mod = IVGMM(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit(iter_limit=100)
    assert res.iterations > 2
    # This is just a quick smoke check of results
    get_all(res)


def test_gmm_cue(data):
    mod = IVGMMCUE(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit()
    assert res.iterations > 2
    mod2 = IVGMM(data.dep, data.exog, data.endog, data.instr)
    res2 = mod2.fit()
    assert res.j_stat.stat <= res2.j_stat.stat

    mod = IVGMMCUE(data.dep, data.exog, data.endog, data.instr, center=False)
    res = mod.fit()
    mod2 = IVGMM(data.dep, data.exog, data.endog, data.instr, center=False)
    res2 = mod2.fit()
    assert res.j_stat.stat <= res2.j_stat.stat


def test_gmm_cue_starting_vals(data):
    mod = IVGMM(data.dep, data.exog, data.endog, data.instr)
    sv = mod.fit().params
    mod = IVGMMCUE(data.dep, data.exog, data.endog, data.instr)
    mod.fit(starting=sv, display=True)

    with pytest.raises(ValueError):
        mod.fit(starting=sv[:-1], display=True)


def test_2sls_just_identified(data):
    mod = IV2SLS(data.dep, data.exog, data.endog, data.instr[:, :2])
    res = mod.fit()
    get_all(res)
    fs = res.first_stage
    stats = fs.diagnostics
    # Fetch again to test cache
    get_all(res)


def test_durbin_smoke(data):
    mod = IV2SLS(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit()
    durb = res.durbin()
    durb2 = res.durbin([mod.endog.cols[1]])


def test_wuhausman_smoke(data):
    mod = IV2SLS(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit()
    wh = res.wu_hausman()
    wh = res.wu_hausman([mod.endog.cols[1]])


def test_wooldridge_smoke(data):
    mod = IV2SLS(data.dep, data.exog, data.endog, data.instr)
    res = mod.fit()
    wr = res.wooldridge_regression

    ws = res.wooldridge_score
    print(wr)
    print(ws)


def test_model_summary_smoke(data):
    res = IV2SLS(data.dep, data.exog, data.endog, data.instr).fit()
    res.__repr__()
    res.__str__()
    res._repr_html_()
    res.summary

    res = _OLS(data.dep, data.exog).fit()
    res.__repr__()
    res.__str__()
    res._repr_html_()
    res.summary


def test_model_missing(data):
    import copy
    data2 = AttrDict()
    for key in data:
        data2[key] = copy.deepcopy(data[key])
    data = data2
    data.dep[::7,:] = np.nan
    data.exog[::13,:] = np.nan
    data.endog[::23,:] = np.nan
    data.instr[::29, :] = np.nan
    res = IV2SLS(data.dep, data.exog, data.endog, data.instr).fit()

    missing = list(map(lambda x: np.any(np.isnan(x),1), [data.dep, data.exog, data.endog, data.instr]))
    missing = np.any(np.c_[missing],0)
    not_missing = missing.shape[0] - missing.sum()
    assert res.nobs == not_missing