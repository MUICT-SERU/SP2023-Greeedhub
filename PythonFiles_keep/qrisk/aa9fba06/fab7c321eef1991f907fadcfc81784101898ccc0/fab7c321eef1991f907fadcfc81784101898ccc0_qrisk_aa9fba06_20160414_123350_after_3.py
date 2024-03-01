from __future__ import division

from unittest import TestCase
from nose_parameterized import parameterized
from numpy.testing import assert_allclose, assert_almost_equal

import numpy as np
import pandas as pd
import pandas.util.testing as pdt

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
    px_list = np.array(
        [10, -10, 10]) / 100.  # Ends in drawdown
    dt = pd.date_range('2000-1-3', periods=3, freq='D')

    px_list_2 = [1.0, 1.2, 1.0, 0.8, 0.7, 0.8, 0.8, 0.8]
    dt_2 = pd.date_range('2000-1-3', periods=8, freq='D')

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
        (simple_rets, stats.DAILY, 0.12271674212427248),
        (simple_week_rets, stats.WEEKLY, 0.055744909991675112),
        (simple_week_rets, stats.WEEKLY, 0.055744909991675112),
        (simple_month_rets, stats.MONTHLY, 0.026778988562993072),
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
        (simple_rets, 1.2333396776895436),
        (np.zeros(10), np.nan),
        ([0.1, 0.2, 0.3], np.nan)
    ])
    def test_sharpe(self, returns, expected):
        assert_almost_equal(
            stats.sharpe_ratio(
                np.asarray(returns)),
            expected, DECIMAL_PLACES)

    @parameterized.expand([
        (pd.Series(px_list_2,
                   index=dt_2).pct_change().dropna(), -2.3992211554712197)
    ])
    def test_calmar(self, returns, expected):
        self.assertEqual(
            stats.calmar_ratio(
                returns),
            expected)

    @parameterized.expand([
        (pd.Series(px_list,
                   index=dt), 0.0, 2.0)
    ])
    def test_omega(self, returns, annual_return_threshhold, expected):
        self.assertEqual(
            stats.omega_ratio(
                returns,
                annual_return_threshhold=annual_return_threshhold),
            expected)

    @parameterized.expand([
        (-simple_rets[:5], -12.29634091915152),
        (-simple_rets, -1.2296340919151518),
        (simple_rets, np.inf)
    ])
    def test_sortino(self, returns, expected):
        self.assertAlmostEqual(
            stats.sortino_ratio(returns),
            expected, DECIMAL_PLACES)

    def test_tail_ratio(self):
        returns = np.random.randn(10000)
        self.assertAlmostEqual(
            stats.tail_ratio(returns),
            1., 1)
