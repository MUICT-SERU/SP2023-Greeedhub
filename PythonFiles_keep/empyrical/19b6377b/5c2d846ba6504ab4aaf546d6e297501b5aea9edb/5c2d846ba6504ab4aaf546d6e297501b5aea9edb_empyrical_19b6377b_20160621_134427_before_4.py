#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import division

from collections import OrderedDict
from functools import partial

import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats


APPROX_BDAYS_PER_MONTH = 21
APPROX_BDAYS_PER_YEAR = 252

MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = 52

DAILY = 'daily'
WEEKLY = 'weekly'
MONTHLY = 'monthly'
YEARLY = 'yearly'

ANNUALIZATION_FACTORS = {
    DAILY: APPROX_BDAYS_PER_YEAR,
    WEEKLY: WEEKS_PER_YEAR,
    MONTHLY: MONTHS_PER_YEAR
}

def cum_returns(returns, starting_value=None):
    """
    Compute cumulative returns from simple returns.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    starting_value : float, optional
       The starting returns (default 1).

    Returns
    -------
    pandas.Series
        Series of cumulative returns.

    Notes
    -----
    For increased numerical accuracy, convert input to log returns
    where it is possible to sum instead of multiplying.
    """

    # df_price.pct_change() adds a nan in first position, we can use
    # that to have cum_returns start at the origin so that
    # df_cum.iloc[0] == starting_value
    # Note that we can't add that ourselves as we don't know which dt
    # to use.
    if pd.isnull(returns.iloc[0]):
        returns.iloc[0] = 0.

    df_cum = np.exp(np.log(1 + returns).cumsum())

    if starting_value is None:
        return df_cum - 1
    else:
        return df_cum * starting_value


def aggregate_returns(df_daily_rets, convert_to):
    """
    Aggregates returns by week, month, or year.

    Parameters
    ----------
    df_daily_rets : pd.Series
       Daily returns of the strategy, noncumulative.
        - See full explanation in tears.create_full_tear_sheet (returns).
    convert_to : str
        Can be 'weekly', 'monthly', or 'yearly'.

    Returns
    -------
    pd.Series
        Aggregated returns.
    """

    def cumulate_returns(x):
        return cum_returns(x)[-1]

    if convert_to == WEEKLY:
        return df_daily_rets.groupby(
            [lambda x: x.year,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == MONTHLY:
        return df_daily_rets.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == YEARLY:
        return df_daily_rets.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError(
            'convert_to must be {}, {} or {}'.format(WEEKLY, MONTHLY, YEARLY)
        )


def var_cov_var_normal(P, c, mu=0, sigma=1):
    """Variance-covariance calculation of daily Value-at-Risk in a
    portfolio.

    Parameters
    ----------
    P : float
        Portfolio value.
    c : float
        Confidence level.
    mu : float, optional
        Mean.

    Returns
    -------
    float
        Variance-covariance.

    """

    alpha = sp.sp.stats.norm.ppf(1 - c, mu, sigma)
    return P - P * (alpha + 1)


def max_drawdown(returns):
    """
    Determines the maximum drawdown of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.

    Returns
    -------
    float
        Maximum drawdown.

    Note
    -----
    See https://en.wikipedia.org/wiki/Drawdown_(economics) for more details.
    """

    if returns.size < 1:
        return np.nan

    df_cum_rets = cum_returns(returns, starting_value=100)
    cum_max_return = df_cum_rets.cummax()

    return df_cum_rets.sub(cum_max_return).div(cum_max_return).min()


def annual_return(returns, period=DAILY):
    """Determines the annual returns of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.

    Returns
    -------
    float
        Annual Return as CAGR (Compounded Annual Growth Rate)

    """

    if returns.size < 1:
        return np.nan

    try:
        ann_factor = ANNUALIZATION_FACTORS[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Must be '{}', '{}', or '{}'".format(
                period, DAILY, WEEKLY, MONTHLY
            )
        )

    num_years = float(len(returns)) / ann_factor
    df_cum_rets = cum_returns(returns, starting_value=100)
    start_value = 100
    end_value = df_cum_rets.iloc[-1]

    total_return = (end_value - start_value) / start_value
    annual_return = (1. + total_return) ** (1 / num_years) - 1

    return annual_return


def annual_volatility(returns, period=DAILY):
    """
    Determines the annual volatility of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing volatility. Can be 'monthly' or 'weekly' or 'daily'.
        - defaults to 'daily'

    Returns
    -------
    float
        Annual volatility.
    """

    if returns.size < 2:
        return np.nan

    try:
        ann_factor = ANNUALIZATION_FACTORS[period]
    except KeyError:
        raise ValueError(
            "period cannot be: '{}'."
            " Must be '{}', '{}', or '{}'".format(
                period, DAILY, WEEKLY, MONTHLY
            )
        )

    return returns.std() * np.sqrt(ann_factor)


def calmar_ratio(returns, period=DAILY):
    """
    Determines the Calmar ratio, or drawdown ratio, of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.


    Returns
    -------
    float
        Calmar ratio (drawdown ratio).

    Note
    -----
    See https://en.wikipedia.org/wiki/Calmar_ratio for more details.
    """

    temp_max_dd = max_drawdown(returns=returns)
    if temp_max_dd < 0:
        temp = annual_return(
            returns=returns,
            period=period
        ) / abs(max_drawdown(returns=returns))
    else:
        return np.nan

    if np.isinf(temp):
        return np.nan

    return temp


def omega_ratio(returns, annual_return_threshhold=0.0):
    """Determines the Omega ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    annual_return_threshold : float, optional
        Threshold over which to consider positive vs negative
        returns. For the ratio, it will be converted to a daily return
        and compared to returns.

    Returns
    -------
    float
        Omega ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/Omega_ratio for more details.

    """

    daily_return_thresh = pow(1 + annual_return_threshhold, 1 /
                              APPROX_BDAYS_PER_YEAR) - 1

    returns_less_thresh = returns - daily_return_thresh

    numer = sum(returns_less_thresh[returns_less_thresh > 0.0])
    denom = -1.0 * sum(returns_less_thresh[returns_less_thresh < 0.0])

    if denom > 0.0:
        return numer / denom
    else:
        return np.nan


def sortino_ratio(returns, required_return=0, period=DAILY):
    """
    Determines the Sortino ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    required_return: float / series
        minimum acceptable return
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.

    Returns
    -------
    depends on input type
    series ==> float
    DataFrame ==> np.array

        Annualized Sortino ratio.

    """
    try:
        ann_factor = ANNUALIZATION_FACTORS[period]
    except KeyError:
        raise ValueError(
            "period cannot be: '{}'."
            " Must be '{}', '{}', or '{}'".format(
                period, DAILY, WEEKLY, MONTHLY
            )
        )

    mu = np.nanmean(returns - required_return, axis=0)
    sortino = mu / downside_risk(returns, required_return)
    if len(returns.shape) == 2:
        sortino = pd.Series(sortino, index=returns.columns)
    return sortino * ann_factor


def downside_risk(returns, required_return=0, period=DAILY):
    """
    Determines the downside deviation below a threshold

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.

    required_return: float / series
        minimum acceptable return
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.

    Returns
    -------
    depends on input type
    series ==> float
    DataFrame ==> np.array

        Annualized downside deviation

    """
    try:
        ann_factor = ANNUALIZATION_FACTORS[period]
    except KeyError:
        raise ValueError(
            "period cannot be: '{}'."
            " Must be '{}', '{}', or '{}'".format(
                period, DAILY, WEEKLY, MONTHLY
            )
        )

    downside_diff = returns - required_return
    mask = downside_diff > 0
    downside_diff[mask] = 0.0
    squares = np.square(downside_diff)
    mean_squares = np.nanmean(squares, axis=0)
    dside_risk = np.sqrt(mean_squares) * np.sqrt(ann_factor)
    if len(returns.shape) == 2:
        dside_risk = pd.Series(dside_risk, index=returns.columns)
    return dside_risk


def sharpe_ratio(returns, risk_free=0, period=DAILY):
    """
    Determines the Sharpe ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.

    Returns
    -------
    float
        Sharpe ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/Sharpe_ratio for more details.
    """

    returns_risk_adj = returns - risk_free

    if (len(returns_risk_adj) < 5) or np.all(returns_risk_adj == 0):
        return np.nan

    return np.mean(returns_risk_adj) / \
        np.std(returns_risk_adj) * \
        np.sqrt(ANNUALIZATION_FACTORS[period])


def information_ratio(returns, factor_returns):
    """
    Determines the Information ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns: float / series

    Returns
    -------
    float
        The information ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/information_ratio for more details.

    """
    active_return = returns - factor_returns
    tracking_error = np.std(active_return, ddof=1)
    if np.isnan(tracking_error):
        return 0.0
    return np.mean(active_return) / tracking_error


def alpha_beta(returns, factor_returns):
    """Calculates both alpha and beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.

    Returns
    -------
    float
        Alpha.
    float
        Beta.

"""

    ret_index = returns.index
    beta, alpha = sp.sp.stats.linregress(factor_returns.loc[ret_index].values,
                                      returns.values)[:2]

    return alpha * APPROX_BDAYS_PER_YEAR, beta


def alpha(returns, factor_returns):
    """Calculates annualized alpha.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.

    Returns
    -------
    float
        Alpha.
"""

    return alpha_beta(returns, factor_returns)[0]


def beta(returns, factor_returns):
    """Calculates beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.

    Returns
    -------
    float
        Beta.
"""

    return alpha_beta(returns, factor_returns)[1]


def stability_of_timeseries(returns):
    """Determines R-squared of a linear fit to the cumulative
    log returns. Computes an ordinary least squares linear fit,
    and returns R-squared.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.

    Returns
    -------
    float
        R-squared.

    """

    cum_log_returns = np.log1p(returns).cumsum()
    rhat = sp.stats.linregress(np.arange(len(cum_log_returns)),
                            cum_log_returns.values)[2]

    return rhat


def tail_ratio(returns):
    """Determines the ratio between the right (95%) and left tail (5%).

    For example, a ratio of 0.25 means that losses are four times
    as bad as profits.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.

    Returns
    -------
    float
        tail ratio

    """

    return np.abs(np.percentile(returns, 95)) / \
        np.abs(np.percentile(returns, 5))


SIMPLE_STAT_FUNCS = [
    annual_return,
    annual_volatility,
    sharpe_ratio,
    calmar_ratio,
    stability_of_timeseries,
    max_drawdown,
    omega_ratio,
    sortino_ratio,
    sp.stats.skew,
    sp.stats.kurtosis,
    tail_ratio,
]

FACTOR_STAT_FUNCS = [
    information_ratio,
    alpha,
    beta,
]
