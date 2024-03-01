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

import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats  # noqa


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


def cum_returns(returns, starting_value=0):
    """
    Compute cumulative returns from simple returns.

    Parameters
    ----------
    returns : pd.Series
        Returns of the strategy as a percentage, noncumulative.
         - Time series with decimal returns.
         - Example:
            2015-07-16    -0.012143
            2015-07-17    0.045350
            2015-07-20    0.030957
            2015-07-21    0.004902.
    starting_value : float, optional
       The starting returns (default is 0).

    Returns
    -------
    pandas.Series
        Series of cumulative returns.

    Notes
    -----
    For increased numerical accuracy, convert input to log returns
    where it is possible to sum instead of multiplying.
    PI((1+r_i)) - 1 = exp(ln(PI(1+r_i)))     # x = exp(ln(x))
                    = exp(SIGMA(ln(1_r_i))   # ln(a*b) = ln(a) + ln(b)
    """

    # df_price.pct_change() adds a nan in first position, we can use
    # that to have cum_logarithmic_returns start at the origin so that
    # df_cum.iloc[0] == starting_value
    # Note that we can't add that ourselves as we don't know which dt
    # to use.
    if pd.isnull(returns.iloc[0]):
        returns.iloc[0] = 0.

    df_cum = np.exp(np.log(1 + returns).cumsum())

    if starting_value is 0:
        return df_cum - 1
    else:
        return df_cum * starting_value


def aggregate_returns(returns, convert_to):
    """
    Aggregates returns by week, month, or year.

    Parameters
    ----------
    returns : pd.Series
       Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
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
        return returns.groupby(
            [lambda x: x.year,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == MONTHLY:
        return returns.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == YEARLY:
        return returns.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError(
            'convert_to must be {}, {} or {}'.format(WEEKLY, MONTHLY, YEARLY)
        )


def max_drawdown(returns):
    """
    Determines the maximum drawdown of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.

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
    drawdown = df_cum_rets.sub(cum_max_return).div(cum_max_return)

    return drawdown.min()


def annual_return(returns, period=DAILY, annualization=ANNUALIZATION_FACTORS):
    """Determines the mean annual growth rate of returns.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.
    annualization : dict, optional
        Factor used to convert the returns into annual returns. The
        annualization factor for daily returns is the number of business days
        in a year, for weekly it is the number of weeks per year, and for
        monthly, it is the number of months per year. Default:
        annualization = {'daily': 252,
                         'weekly': 52,
                         'monthly': 12}

    Returns
    -------
    float
        Annual Return as CAGR (Compounded Annual Growth Rate).

    """

    if returns.size < 1:
        return np.nan

    try:
        ann_factor = annualization[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Can be '{}'.".format(
                period, "', '".join(annualization.keys())
            )
        )

    num_years = float(len(returns)) / ann_factor
    start_value = 100
    end_value = cum_returns(returns, starting_value=start_value).iloc[-1]
    total_return = (end_value - start_value) / start_value
    annual_return = pow((1. + total_return), (1 / num_years)) - 1

    return annual_return


def annual_volatility(returns, period=DAILY, alpha=2.0,
                      annualization=ANNUALIZATION_FACTORS):
    """
    Determines the annual volatility of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    period : str, optional
        - Defines the periodicity of the 'returns' data for purposes of
        annualizing volatility. Can be 'monthly' or 'weekly' or 'daily'.
        - defaults to 'daily'
    alpha : float, optional
        Scaling relation (Levy stability exponent).
        - Defaults to Weiner process scaling of 2.
    annualization : dict, optional
        Factor used to convert returns into annual returns.
        - See full explanation in annual_return.

    Returns
    -------
    float
        Annual volatility.
    """

    if returns.size < 2:
        return np.nan

    try:
        ann_factor = annualization[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Can be '{}'.".format(
                period, "', '".join(annualization.keys())
            )
        )

    volatility = returns.std() * pow(ann_factor, float(1.0/alpha))

    return volatility


def calmar_ratio(returns, period=DAILY, annualization=ANNUALIZATION_FACTORS):
    """
    Determines the Calmar ratio, or drawdown ratio, of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cumf_returns.
    period : str, optional
        - Defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - Defaults to 'daily'.
    annualization : dict, optional
        Factor used to convert returns into annual returns.
        - See full explanation in annual_return.


    Returns
    -------
    float, np.nan
        Calmar ratio (drawdown ratio) as float. Returns np.nan if there is no
        calmar ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/Calmar_ratio for more details.
    """

    temp_max_dd = max_drawdown(returns=returns)
    if temp_max_dd < 0:
        temp = annual_return(
            returns=returns,
            period=period,
            annualization=annualization
        ) / abs(max_drawdown(returns=returns))
    else:
        return np.nan

    if np.isinf(temp):
        return np.nan

    return temp


def omega_ratio(returns, minimum_acceptable_return=0.0,
                bdays=APPROX_BDAYS_PER_YEAR):
    """Determines the Omega ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    minimum_acceptable_return : float, optional
        Minimum acceptance return of the investor. Threshold over which to
        consider positive vs negative returns. For the ratio, it will be
        converted to a daily return and compared to returns.
        - Default is 0.
    bdays : int, optional
        Number of business days in a year.
        - Default is 252.

    Returns
    -------
    float
        Omega ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/Omega_ratio for more details.

    """

    daily_return_thresh = pow(1 + minimum_acceptable_return, 1 / bdays) - 1

    returns_less_thresh = returns - daily_return_thresh

    numer = sum(returns_less_thresh[returns_less_thresh > 0.0])
    denom = -1.0 * sum(returns_less_thresh[returns_less_thresh < 0.0])

    if denom > 0.0:
        return numer / denom
    else:
        return np.nan


def sharpe_ratio(returns, risk_free=0, period=DAILY,
                 annualization=ANNUALIZATION_FACTORS):
    """
    Determines the Sharpe ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    risk_free : int, float
        Constant risk-free return throughout the period.
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.
    annualization : dict, optional
        Factor used to convert returns into annual returns.
        - See full explanation in annual_return.

    Returns
    -------
    float
        Sharpe ratio.
    np.nan
        If insufficient length of returns or if if adjusted returns are 0.

    Note
    -----
    See https://en.wikipedia.org/wiki/Sharpe_ratio for more details.

    """

    try:
        ann_factor = annualization[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Can be '{}'.".format(
                period, "', '".join(annualization.keys())
            )
        )

    returns_risk_adj = returns - risk_free

    if (len(returns_risk_adj) < 5) or np.all(returns_risk_adj == 0):
        return np.nan

    return np.mean(returns_risk_adj) / np.std(returns_risk_adj, ddof=1) * \
        np.sqrt(ann_factor)


def sortino_ratio(returns, required_return=0, period=DAILY,
                  annualization=ANNUALIZATION_FACTORS):
    """
    Determines the Sortino ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    required_return: float / series
        minimum acceptable return
    period : str, optional
        - Defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily' or another value
        if a custom annualization factor is used.
        - defaults to 'daily'.
    annualization : dict, optional
        Factor used to convert returns into annual returns.
        - See full explanation in annual_return.

    Returns
    -------
    depends on input type
    series ==> float
    DataFrame ==> np.array

        Annualized Sortino ratio.

    """

    try:
        ann_factor = annualization[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Can be '{}'.".format(
                period, "', '".join(annualization.keys())
            )
        )

    if len(returns) < 2:
        return np.nan

    mu = np.nanmean(returns - required_return, axis=0)
    sortino = mu / downside_risk(returns, required_return)
    if len(returns.shape) == 2:
        sortino = pd.Series(sortino, index=returns.columns)
    return sortino * ann_factor


def downside_risk(returns, required_return=0, period=DAILY,
                  annualization=ANNUALIZATION_FACTORS):
    """
    Determines the downside deviation below a threshold

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    required_return: float / series
        minimum acceptable return
    period : str, optional
        - defines the periodicity of the 'returns' data for purposes of
        annualizing. Can be 'monthly', 'weekly', or 'daily'
        - defaults to 'daily'.
    annualization : dict, optional
        Factor used to convert returns into annual returns.
        - See full explanation in annual_return.

    Returns
    -------
    depends on input type
    series ==> float
    DataFrame ==> np.array

        Annualized downside deviation

    """

    try:
        ann_factor = annualization[period]
    except KeyError:
        raise ValueError(
            "period cannot be '{}'. "
            "Can be '{}'.".format(
                period, "', '".join(annualization.keys())
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


def information_ratio(returns, factor_returns):
    """
    Determines the Information ratio of a strategy.

    Parameters
    ----------
    returns : pd.Series or pd.DataFrame
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    factor_returns: float / series
        Benchmark return to compare returns against.

    Returns
    -------
    float
        The information ratio.

    Note
    -----
    See https://en.wikipedia.org/wiki/information_ratio for more details.

    """
    if len(returns) < 2:
        return np.nan

    active_return = returns - factor_returns
    tracking_error = np.std(active_return, ddof=1)
    if np.isnan(tracking_error):
        return 0.0
    return np.mean(active_return) / tracking_error


def alpha_beta(returns, factor_returns, risk_free=0.0):
    """Calculates both alpha and beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.
    risk_free : int, float, optional
        Constant risk-free return throughout the period. For example, the
        interest rate on a three month us treasury bill.
        - Default is 0.

    Returns
    -------
    float
        Alpha.
    float
        Beta.

    """
    if len(returns) < 2:
        return np.nan

    y = (returns - risk_free).loc[factor_returns.index].dropna()
    x = (factor_returns - risk_free).loc[y.index].dropna()
    y = y.loc[x.index]
    beta, alpha = sp.stats.linregress(x.values, y.values)[:2]

    return alpha, beta


def alpha(returns, factor_returns, risk_free=0.0):
    """Calculates alpha.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.
    risk_free : int, float, optional
        Constant risk-free return throughout the period. For example, the
        interest rate on a three month us treasury bill.
        - Default is 0.

    Returns
    -------
    float
        Alpha.
    """

    if len(returns) < 2:
        return np.nan
    return alpha_beta(returns, factor_returns, risk_free=risk_free)[0]


def beta(returns, factor_returns, risk_free=0.0):
    """Calculates beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.
    factor_returns : pd.Series
         Daily noncumulative returns of the factor to which beta is
         computed. Usually a benchmark such as the market.
         - This is in the same style as returns.
    risk_free : int, float, optional
        Constant risk-free return throughout the period. For example, the
        interest rate on a three month us treasury bill.
        - Default is 0.

    Returns
    -------
    float
        Beta.
    """

    if len(returns) < 2:
        return np.nan
    return alpha_beta(returns, factor_returns, risk_free=risk_free)[1]


def stability_of_timeseries(returns):
    """Determines R-squared of a linear fit to the cumulative
    log returns. Computes an ordinary least squares linear fit,
    and returns R-squared.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
        - See full explanation in cum_returns.

    Returns
    -------
    float
        R-squared.

    """
    if len(returns) < 2:
        return np.nan
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
         - See full explanation in cum_returns.

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
