from __future__ import division

from unittest import TestCase
from nose_parameterized import parameterized
from numpy.testing import assert_almost_equal

import numpy as np
import pandas as pd

from .. import stats

DECIMAL_PLACES = 8


class TestStats(TestCase):
    simple_rets = pd.Series(
        [0.1] * 3 + [0] * 497,
        pd.date_range(
            '2000-1-3',
            periods=500,
            freq='D'))

    simple_week_rets = pd.Series(
        [0.1] * 3 + [0] * 497,
        pd.date_range(
            '2000-1-31',
            periods=500,
            freq='W'))

    simple_month_rets = pd.Series(
        [0.1] * 3 + [0] * 497,
        pd.date_range(
            '2000-1-31',
            periods=500,
            freq='M'))

    simple_benchmark = pd.Series(
        [0.03] * 4 + [0] * 496,
        pd.date_range(
            '2000-1-1',
            periods=500,
            freq='D'))

    s_1 = pd.Series(np.array([10, -10, 10]) / 100.,
                    index=pd.date_range('2000-1-3', periods=3, freq='D'))

    s_2 = pd.Series([1.0, 1.2, 1.0, 0.8, 0.7, 0.8, 0.8, 0.8],
                    index=pd.date_range('2000-1-3', periods=8, freq='D'))

    s_3 = pd.Series(np.array([1, 10, -2, 2, 3, 2, 1, -10])/100,
                    index=pd.date_range('2000-1-3', periods=8, freq='D'))

    one = [-0.00171614, 0.01322056, 0.03063862, -0.01422057, -0.00489779,
           0.01268925, -0.03357711, 0.01797036]
    two = [0.01846232, 0.00793951, -0.01448395, 0.00422537, -0.00339611,
           0.03756813, 0.0151531, 0.03549769]
    df_index_simple = pd.date_range('2000-1-3', periods=8, freq='D')
    df_index_week = pd.date_range('2000-1-3', periods=8, freq='W')
    df_index_month = pd.date_range('2000-1-3', periods=8, freq='M')

    d_simple = {'one': pd.Series(one, index=df_index_simple),
                'two': pd.Series(two, index=df_index_simple)}
    df_simple = pd.DataFrame(d_simple)

    d_week = {'one': pd.Series(one, index=df_index_week),
              'two': pd.Series(two, index=df_index_week)}
    df_week = pd.DataFrame(d_week)

    d_month = {'one': pd.Series(one, index=df_index_month),
               'two': pd.Series(two, index=df_index_month)}
    df_month = pd.DataFrame(d_month)

    @parameterized.expand([
        (simple_rets, 0, 0.33100000000000041),
        (simple_week_rets, 100, 133.10000000000005),
        (simple_benchmark, 100, 112.55088100000002)
    ])
    def test_cum_returns(self, returns, starting_value, expected):
        self.assertEqual(
            stats.cum_returns(
                returns, starting_value
            )[-1],
            expected)

    @parameterized.expand([
        (simple_rets, stats.WEEKLY, 72),
        (simple_rets, stats.MONTHLY, 17),
        (simple_rets, stats.YEARLY, 2),
        (simple_week_rets, stats.WEEKLY, 499),
        (simple_week_rets, stats.YEARLY, 10),
        (simple_month_rets, stats.YEARLY, 42)
    ])
    def test_aggregate_returns(self, returns, convert_to, expected):
        self.assertEqual(
            len(stats.aggregate_returns(returns, convert_to)),
            expected)

    @parameterized.expand([
        (simple_rets, 0.0),
        (s_3, -0.10000000000000002)
    ])
    def test_max_drawdown(self, returns, expected):
        self.assertEqual(
            stats.max_drawdown(
                returns
            ),
            expected)

    @parameterized.expand([
        (simple_rets, stats.DAILY, 0.15500998835658075),
        (simple_week_rets, stats.WEEKLY, 0.030183329386562319),
        (simple_month_rets, stats.MONTHLY, 0.006885932704891129)
    ])
    def test_annual_ret(self, returns, period, expected):
        self.assertEqual(
            stats.annual_return(
                returns,
                period=period
            ),
            expected)

    @parameterized.expand([
        (simple_rets, stats.DAILY, 0.12271674212427248),
        (simple_week_rets, stats.WEEKLY, 0.055744909991675112),
        (simple_month_rets, stats.MONTHLY, 0.026778988562993072)
    ])
    def test_annual_volatility(self, returns, period, expected):
        self.assertAlmostEqual(
            stats.annual_volatility(
                returns,
                period=period
            ),
            expected,
            DECIMAL_PLACES
        )

    @parameterized.expand([
        (s_2.pct_change().dropna(), -2.3992211554712197)
    ])
    def test_calmar(self, returns, expected):
        self.assertEqual(
            stats.calmar_ratio(
                returns),
            expected)

    @parameterized.expand([
        (s_1, 0.0, 2.0)
    ])
    def test_omega(self, returns, minimum_acceptable_return, expected):
        self.assertEqual(
            stats.omega_ratio(
                returns,
                minimum_acceptable_return=minimum_acceptable_return),
            expected)

    @parameterized.expand([
        (simple_rets, 1.2321057207245873),
        (np.zeros(10), np.nan),
        ([0.1, 0.2, 0.3], np.nan)
    ])
    def test_sharpe_ratio(self, returns, expected):
        assert_almost_equal(
            stats.sharpe_ratio(
                np.asarray(returns)),
            expected, DECIMAL_PLACES)

    @parameterized.expand([
        (simple_rets, 0.0, stats.DAILY, 0.0),
        (simple_week_rets, 0.0, stats.WEEKLY, 0.0),
        (simple_month_rets, 0.0, stats.MONTHLY, 0.0),
        (simple_rets, 0.1, stats.DAILY, 1.5826812692390093),
        (simple_week_rets, 0.1, stats.WEEKLY, 0.718943669559723),
        (simple_month_rets, 0.1, stats.MONTHLY, 0.3453693674893592),
        (df_simple, 0.0, stats.DAILY,
         pd.Series([0.20671788246185202, 0.083495680595704475],
                   index=['one', 'two'])),
        (df_week, 0.0, stats.WEEKLY,
         pd.Series([0.093902996054410062, 0.037928477556776516],
                   index=['one', 'two'])),
        (df_month, 0.0, stats.MONTHLY,
         pd.Series([0.045109540184877193, 0.018220251263412916],
                   index=['one', 'two']))
    ])
    def test_downside_risk(self, returns, required_return, period, expected):
        self.assertTrue(
            np.all(
                stats.downside_risk(
                    returns,
                    required_return=required_return,
                    period=period) == expected))

    @parameterized.expand([
        (-simple_rets[:5], 0.0, stats.DAILY, -12.29634091915152),
        (-simple_rets, 0.0, stats.DAILY, -1.2296340919151518),
        (simple_rets, 0.0, stats.DAILY, np.inf),
        (df_simple, 0.0, stats.DAILY,
         pd.Series([3.0639640966566306, 38.090963117002495],
                   index=['one', 'two'])),
        (df_week, 0.0, stats.WEEKLY,
         pd.Series([0.63224655962755871, 7.8600400082703556],
                   index=['one', 'two'])),
        (df_month, 0.0, stats.MONTHLY,
         pd.Series([0.14590305222174432, 1.8138553865239282],
                   index=['one', 'two']))

    ])
    def test_sortino(self, returns, required_return, period, expected):
        self.assertTrue(
            np.all(
                stats.sortino_ratio(
                    returns,
                    required_return=required_return,
                    period=period) == expected))

    @parameterized.expand([
        (simple_rets, simple_benchmark, 0.076577237215895003)
    ])
    def test_information_ratio(self, returns, factor_returns, expected):
        assert_almost_equal(
            stats.information_ratio(returns, factor_returns),
            expected,
            DECIMAL_PLACES)

    @parameterized.expand([
        (simple_rets, simple_benchmark, (0.00020161290322580659,
                                         3.3266129032258061))
    ])
    def test_alpha_beta(self, returns, benchmark, expected):
        self.assertEqual(
            stats.alpha_beta(returns, benchmark),
            expected)

    @parameterized.expand([
        (simple_rets, simple_benchmark, 0.00020161290322580659)
    ])
    def test_alpha(self, returns, benchmark, expected):
        self.assertEqual(
            stats.alpha(returns, benchmark),
            expected)

    @parameterized.expand([
        (simple_rets, simple_benchmark, 3.3266129032258061)
    ])
    def test_beta(self, returns, benchmark, expected):
        self.assertEqual(
            stats.beta(returns, benchmark),
            expected)

    @parameterized.expand([
        (s_1, -0.086422992657049696),
        (s_2, 0.99845165832382166),
        (s_3, 0.49842309053331446)
    ])
    def test_stability_of_timeseries(self, returns, expected):
        self.assertEqual(
            stats.stability_of_timeseries(returns),
            expected)

    @parameterized.expand([
        (np.random.randn(10000), 1.)
    ])
    def test_tail_ratio(self, returns, expected):
        self.assertAlmostEqual(
            stats.tail_ratio(returns),
            expected, 1)
