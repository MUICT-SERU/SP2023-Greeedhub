import numpy as np
import pytest

from panel.iv import IV2SLS, IVGMM, IVLIML, IVGMMCUE


def get_all(v):
    attr = [d for d in dir(v) if not d.startswith('_')]
    for a in attr:
        getattr(v, a)


class TestIV(object):
    @classmethod
    def setup_class(cls):
        np.random.seed(12345)
        t, k, m = 5000, 3, 3
        beta = np.arange(1, k + 1)[:, None]
        cls.x = np.random.standard_normal((t, k))
        cls.e = np.random.standard_normal((t, 1))
        cls.z = np.random.standard_normal((t, m))
        cls.x[:, 0] = cls.x[:, 0] + cls.e[:, 0] + cls.z.sum(axis=1)
        cls.x_endog = cls.x[:, [0]]
        cls.x_exog = cls.x[:, 1:]
        cls.y = cls.x @ beta + cls.e

    def test_iv2sls_smoke(self):
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)
        mod.fit()

    def test_fake_ols_smoke(self):
        print('2SLS')
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)
        res = mod.fit()
        print(res.params)
        print('OLS')
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.x_endog)
        res = mod.fit()
        print(res.params)

    def test_iv2sls_smoke_homoskedastic(self):
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)
        mod.fit(cov_type='unadjusted')

    def test_iv2sls_smoke_cov_config(self):
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)
        mod.fit(cov_type='unadjusted', debiased=True)

    def test_iv2sls_smoke_nw(self):
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)
        mod.fit(cov_type='kernel', kernel='newey-west')
        mod.fit(cov_type='kernel', kernel='bartlett')
        mod.fit(cov_type='kernel', kernel='parzen')
        mod.fit(cov_type='kernel', kernel='qs')

    def test_iv2sls_smoke_cluster(self):
        mod = IV2SLS(self.y, self.x_exog, self.x_endog, self.z)

        clusters = np.tile(np.arange(5), (self.y.shape[0] // 5,)).ravel()
        mod.fit(cov_type='one-way', clusters=clusters)

        clusters = np.tile(np.arange(100), (self.y.shape[0] // 100,)).ravel()
        mod.fit(cov_type='one-way', clusters=clusters)

        clusters = np.tile(np.arange(500), (self.y.shape[0] // 500,)).ravel()
        mod.fit(cov_type='one-way', clusters=clusters)

        clusters = np.tile(np.arange(1000), (self.y.shape[0] // 1000,)).ravel()
        mod.fit(cov_type='one-way', clusters=clusters)

        clusters = np.tile(np.arange(2500), (self.y.shape[0] // 2500,)).ravel()
        mod.fit(cov_type='one-way', clusters=clusters)

        res = mod.fit(cov_type='one-way')
        get_all(res)

    def test_ivgmm_smoke(self):
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z)
        mod.fit()

    def test_ivgmm_smoke_iter(self):
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z)
        res = mod.fit(iter_limit=100)

    def test_ivgmm_smoke_weights(self):
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='unadjusted')
        mod.fit()

        with pytest.raises(ValueError):
            IVGMM(self.y, self.x_exog, self.x_endog, self.z, bw=20)

    def test_ivgmm_kernel_smoke(self):
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='kernel')
        mod.fit()

        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='kernel', kernel='parzen')
        mod.fit()

        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='kernel', kernel='qs')
        mod.fit()

    def test_ivgmm_cluster_smoke(self):
        k = 500
        clusters = np.tile(np.arange(k), (self.y.shape[0] // k, 1)).ravel()
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='clustered',
                    clusters=clusters)
        mod.fit()

    def test_ivgmm_cluster_is(self):
        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z, weight_type='clustered',
                    clusters=np.arange(self.y.shape[0]))
        mod.fit()

        mod = IVGMM(self.y, self.x_exog, self.x_endog, self.z)
        res = mod.fit()
        get_all(res)

    def test_ivliml_smoke(self):
        mod = IVLIML(self.y, self.x_exog, self.x_endog, self.z)
        res = mod.fit()
        get_all(res)

    def test_ivgmmcue_smoke(self):
        mod = IVGMMCUE(self.y, self.x_exog, self.x_endog, self.z)
        res = gmod.fit()
        get_all(res)
