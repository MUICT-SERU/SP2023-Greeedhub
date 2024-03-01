from __future__ import division

from unittest import TestCase
from nose_parameterized import parameterized
from numpy.testing import assert_almost_equal

import numpy as np
import pandas as pd

import qrisk

DECIMAL_PLACES = 8


class TestStats(TestCase):

    # Simple benchmark, no drawdown
    simple_benchmark = pd.Series(
        np.array([1., 1., 1., 1., 1., 1., 1., 1., 1.]) / 100,
        index=pd.date_range('2000-1-30', periods=9, freq='D'))

    # All positive returns, small variance
    positive_returns = pd.Series(
        np.array([1., 2., 1., 1., 1., 1., 1., 1., 1.]) / 100,
        index=pd.date_range('2000-1-30', periods=9, freq='D'))

    # All negative returns
    negative_returns = pd.Series(
        np.array([0., -6., -7., -1., -9., -2., -6., -8., -5.]) / 100,
        index=pd.date_range('2000-1-30', periods=9, freq='D'))

    # Positive and negative returns with max drawdown
    mixed_returns = pd.Series(
        np.array([np.nan, 1., 10., -4., 2., 3., 2., 1., -10.]) / 100,
        index=pd.date_range('2000-1-30', periods=9, freq='D'))

    # Weekly returns
    weekly_returns = pd.Series(
        np.array([0., 1., 10., -4., 2., 3., 2., 1., -10.])/100,
        index=pd.date_range('2000-1-30', periods=9, freq='W'))

    # Monthly returns
    monthly_returns = pd.Series(
        np.array([0., 1., 10., -4., 2., 3., 2., 1., -10.])/100,
        index=pd.date_range('2000-1-30', periods=9, freq='M'))

    # Series of length 1
    one_return = pd.Series(
        np.array([1.])/100,
        index=pd.date_range('2000-1-30', periods=1, freq='D'))

    # Empty series
    empty_returns = pd.Series(
        np.array([])/100,
        index=pd.date_range('2000-1-30', periods=0, freq='D'))

    one = [-0.00171614, 0.01322056, 0.03063862, -0.01422057, -0.00489779,
           0.01268925, -0.03357711, 0.01797036]
    two = [0.01846232, 0.00793951, -0.01448395, 0.00422537, -0.00339611,
           0.03756813, 0.0151531, 0.03549769]

    df_index_simple = pd.date_range('2000-1-30', periods=8, freq='D')
    df_index_week = pd.date_range('2000-1-30', periods=8, freq='W')
    df_index_month = pd.date_range('2000-1-30', periods=8, freq='M')

    df_simple = pd.DataFrame({
        'one': pd.Series(one, index=df_index_simple),
        'two': pd.Series(two, index=df_index_simple)})

    df_week = pd.DataFrame({
        'one': pd.Series(one, index=df_index_week),
        'two': pd.Series(two, index=df_index_week)})

    df_month = pd.DataFrame({
        'one': pd.Series(one, index=df_index_month),
        'two': pd.Series(two, index=df_index_month)})

    @parameterized.expand([
        (mixed_returns, 0, [0.0, 0.01, 0.111, 0.066559, 0.08789, 0.12052,
                            0.14293, 0.15436, 0.03893]),
        (mixed_returns, 100, [100.0, 101.0, 111.1, 106.65599, 108.78912,
                              112.05279, 114.29384, 115.43678, 103.89310]),
        (negative_returns, 0, [0.0, -0.06, -0.1258, -0.13454, -0.21243,
                               -0.22818, -0.27449, -0.33253, -0.36590])
    ])
    def test_cum_returns(self, returns, starting_value, expected):
        cum_returns = qrisk.cum_returns(returns, starting_value=starting_value)
        for i in range(returns.size):
            assert_almost_equal(
                cum_returns[i],
                expected[i],
                4)

    @parameterized.expand([
        (simple_benchmark, qrisk.WEEKLY, [0.010000000000000009,
                                          0.072135352107010053,
                                          0.010000000000000009]),
        (simple_benchmark, qrisk.MONTHLY, [0.020100000000000007,
                                           0.072135352107010053]),
        (simple_benchmark, qrisk.YEARLY, [0.093685272684361109]),
        (weekly_returns, qrisk.MONTHLY, [0.0, 0.087891200000000058,
                                         -0.04500459999999995]),
        (weekly_returns, qrisk.YEARLY, [0.038931091700480147]),
        (monthly_returns, qrisk.YEARLY, [0.038931091700480147])
    ])
    def test_aggregate_returns(self, returns, convert_to, expected):
        returns = qrisk.aggregate_returns(returns, convert_to).values.tolist()
        for i, v in enumerate(returns):
            assert_almost_equal(
                v,
                expected[i],
                DECIMAL_PLACES)

    @parameterized.expand([
        (simple_benchmark, 0.0),
        (mixed_returns, -0.1),
        (positive_returns, -0.0),
        (negative_returns, -0.36590730349873601),
        (one_return, 0.0),
        (empty_returns, np.nan)
    ])
    def test_max_drawdown(self, returns, expected):
        assert_almost_equal(
            qrisk.max_drawdown(
                returns
            ),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (mixed_returns, qrisk.DAILY, 1.9135925373194231),
        (weekly_returns, qrisk.WEEKLY, 0.24690830513998208),
        (monthly_returns, qrisk.MONTHLY, 0.052242061386048144)
    ])
    def test_annual_ret(self, returns, period, expected):
        assert_almost_equal(
            qrisk.annual_return(
                returns,
                period=period
            ),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (simple_benchmark, qrisk.DAILY, 0.0),
        (mixed_returns, qrisk.DAILY, 0.85527773266933604),
        (weekly_returns, qrisk.WEEKLY, 0.38851569394870583),
        (monthly_returns, qrisk.MONTHLY, 0.18663690238892558)
    ])
    def test_annual_volatility(self, returns, period, expected):
        assert_almost_equal(
            qrisk.annual_volatility(
                returns,
                period=period
            ),
            expected,
            DECIMAL_PLACES
        )

    @parameterized.expand([
        (empty_returns, qrisk.DAILY, np.nan),
        (one_return, qrisk.DAILY, np.nan),
        (mixed_returns, qrisk.DAILY, 19.135925373194233),
        (weekly_returns, qrisk.WEEKLY, 2.4690830513998208),
        (monthly_returns, qrisk.MONTHLY, 0.52242061386048144)
    ])
    def test_calmar(self, returns, period, expected):
        assert_almost_equal(
            qrisk.calmar_ratio(
                returns,
                period=period
            ),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, 0.0, 0.0, np.nan),
        (one_return, 0.0, 0.0, np.nan),
        (mixed_returns, 0.0, 10.0, 0.78629772289706013),
        (mixed_returns, 0.0, -10.0, np.nan),
        (mixed_returns, simple_benchmark, 0.0, 0.76470588235294112),
        (positive_returns, 0.01, 0.0, np.nan),
        (positive_returns, 0.011, 0.0, 1.125),
        (positive_returns, 0.02, 0.0, 0.0),
        (negative_returns, 0.01, 0.0, 0.0)
    ])
    def test_omega(self, returns, risk_free, required_return,
                   expected):
        assert_almost_equal(
            qrisk.omega_ratio(
                returns,
                risk_free=risk_free,
                required_return=required_return),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, 0.0, np.nan),
        (one_return, 0.0, np.nan),
        (mixed_returns, 0.0, 1.6368951821422701),
        (mixed_returns, simple_benchmark, -1.3095161457138154),
        (positive_returns, 0.0, 52.915026221291804),
        (negative_returns, 0.0, -24.406808633910085)
    ])
    def test_sharpe_ratio(self, returns, risk_free, expected):
        assert_almost_equal(
            qrisk.sharpe_ratio(
                np.asarray(returns),
                risk_free=risk_free),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, 0.0, qrisk.DAILY, np.nan),
        (one_return, 0.0, qrisk.DAILY, 0.0),
        (mixed_returns, 0.0, qrisk.DAILY, 0.5699122739510003),
        (mixed_returns, 0.1, qrisk.DAILY, 1.7023513150933332),
        (weekly_returns, 0.0, qrisk.WEEKLY, 0.25888650451930134),
        (weekly_returns, 0.1, qrisk.WEEKLY, 0.7733045971672482),
        (monthly_returns, 0.0, qrisk.MONTHLY, 0.1243650540411842),
        (monthly_returns, 0.1, qrisk.MONTHLY, 0.37148351242013422),
        (df_simple, 0.0, qrisk.DAILY,
         pd.Series([0.20671788246185202, 0.083495680595704475],
                   index=['one', 'two'])),
        (df_week, 0.0, qrisk.WEEKLY,
         pd.Series([0.093902996054410062, 0.037928477556776516],
                   index=['one', 'two'])),
        (df_month, 0.0, qrisk.MONTHLY,
         pd.Series([0.045109540184877193, 0.018220251263412916],
                   index=['one', 'two']))
    ])
    def test_downside_risk(self, returns, required_return, period, expected):
        downside_risk = qrisk.downside_risk(
                        returns,
                        required_return=required_return,
                        period=period)
        if isinstance(downside_risk, float):
            assert_almost_equal(
                downside_risk,
                expected,
                DECIMAL_PLACES)
        else:
            for i in range(downside_risk.size):
                assert_almost_equal(
                    downside_risk[i],
                    expected[i],
                    DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, 0.0, qrisk.DAILY, np.nan),
        (one_return, 0.0, qrisk.DAILY, np.nan),
        (mixed_returns, 0.0, qrisk.DAILY, 2.456518422202588),
        (mixed_returns, simple_benchmark, qrisk.DAILY, -1.7457431218879385),
        (positive_returns, 0.0, qrisk.DAILY, np.inf),
        (negative_returns, 0.0, qrisk.DAILY, -13.532743075043401),
        (simple_benchmark, 0.0, qrisk.DAILY, np.inf),
        (weekly_returns, 0.0, qrisk.WEEKLY, 0.50690062680370862),
        (monthly_returns, 0.0, qrisk.MONTHLY, 0.11697706772393276),
        (df_simple, 0.0, qrisk.DAILY,
         pd.Series([3.0639640966566306, 38.090963117002495],
                   index=['one', 'two'])),
        (df_week, 0.0, qrisk.WEEKLY,
         pd.Series([0.63224655962755871, 7.8600400082703556],
                   index=['one', 'two'])),
        (df_month, 0.0, qrisk.MONTHLY,
         pd.Series([0.14590305222174432, 1.8138553865239282],
                   index=['one', 'two']))
    ])
    def test_sortino(self, returns, required_return, period, expected):
        sortino_ratio = qrisk.sortino_ratio(
                        returns,
                        required_return=required_return,
                        period=period)
        if isinstance(sortino_ratio, float):
            assert_almost_equal(
                sortino_ratio,
                expected,
                DECIMAL_PLACES)
        else:
            for i in range(sortino_ratio.size):
                assert_almost_equal(
                    sortino_ratio[i],
                    expected[i],
                    DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, 0.0, np.nan),
        (one_return, 0.0, np.nan),
        (positive_returns, 0.0, 3.3333333333333326),
        (negative_returns, 0.0, -1.5374844271921471),
        (mixed_returns, 0.0, 0.10311470414829102),
        (mixed_returns, simple_benchmark, -0.082491763318632769),
        (simple_benchmark, simple_benchmark, np.nan),
    ])
    def test_information_ratio(self, returns, factor_returns, expected):
        assert_almost_equal(
            qrisk.information_ratio(returns, factor_returns),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, simple_benchmark, (np.nan, np.nan)),
        (one_return, one_return, (np.nan, np.nan)),
        (mixed_returns, simple_benchmark, (np.nan, np.nan)),
        (mixed_returns, negative_returns, (-8.3066666666666666,
                                           -0.71296296296296291)),
        (mixed_returns, mixed_returns, (0.0, 1.0)),
        (mixed_returns, -mixed_returns, (0.0, -1.0)),
    ])
    def test_alpha_beta(self, returns, benchmark, expected):
        assert_almost_equal(
            qrisk.alpha_beta(returns, benchmark)[0],
            expected[0],
            DECIMAL_PLACES)
        assert_almost_equal(
            qrisk.alpha_beta(returns, benchmark)[1],
            expected[1],
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, simple_benchmark, np.nan),
        (one_return, one_return, np.nan),
        (mixed_returns, simple_benchmark, np.nan),
        (mixed_returns, mixed_returns, 0.0),
        (mixed_returns, -mixed_returns, 0.0),
    ])
    def test_alpha(self, returns, benchmark, expected):
        assert_almost_equal(
            qrisk.alpha(returns, benchmark),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, simple_benchmark, np.nan),
        (one_return, one_return,  np.nan),
        (mixed_returns, simple_benchmark, np.nan),
        (mixed_returns, mixed_returns, 1.0),
        (mixed_returns, -mixed_returns, -1.0),
    ])
    def test_beta(self, returns, benchmark, expected):
        assert_almost_equal(
            qrisk.beta(returns, benchmark),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, simple_benchmark),
        (one_return, one_return),
        (mixed_returns, simple_benchmark),
        (mixed_returns, negative_returns),
        (mixed_returns, mixed_returns),
        (mixed_returns, -mixed_returns),
    ])
    def test_alpha_beta_equality(self, returns, benchmark):
        alpha_beta = qrisk.alpha_beta(returns, benchmark)
        assert_almost_equal(
            alpha_beta[0],
            qrisk.alpha(returns, benchmark),
            DECIMAL_PLACES)
        assert_almost_equal(
            alpha_beta[1],
            qrisk.beta(returns, benchmark),
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, np.nan),
        (one_return, np.nan),
        (mixed_returns, 0.33072113092134847),
        (simple_benchmark, 1.0),
    ])
    def test_stability_of_timeseries(self, returns, expected):
        assert_almost_equal(
            qrisk.stability_of_timeseries(returns),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (empty_returns, np.nan),
        (one_return, 1.0),
        (mixed_returns, 0.9473684210526313),
        (np.random.randn(100000), 1.),
    ])
    def test_tail_ratio(self, returns, expected):
        assert_almost_equal(
            qrisk.tail_ratio(returns),
            expected,
            1)
