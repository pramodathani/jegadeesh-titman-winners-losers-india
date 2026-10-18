"""Section III: where the relative strength profits come from."""

import numpy as np
import pandas as pd
import statsmodels.api as statsmodels_api
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.event_time import EventTimeReturns
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class SectionThree:
    """The weighted relative strength strategy and the lead-lag test.

    Attributes:
        statistics: The return statistics helper.
    """

    def __init__(self) -> None:
        """Creates the helper.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.statistics = ReturnStatistics()

    def half_year_returns(
        self,
        monthly_returns: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compounds monthly returns over January-June and July-December.

        A share has a half-year return only when it has all six monthly
        returns and was eligible in the last month of the half-year.

        Args:
            monthly_returns: Monthly returns, months by shares.
            eligible: Bools, months by shares.

        Returns:
            Half-year returns, indexed by the half-year's last month.

        Raises:
            None.
        """
        logs = np.log1p(monthly_returns)
        summed = logs.rolling(6, min_periods=6).sum()
        ends = summed.index[summed.index.month.isin([6, 12])]
        half = np.expm1(summed.loc[ends])
        return half.where(eligible.reindex_like(half))

    def wrss_profit(self, previous: pd.Series, current: pd.Series) -> float:
        """Gives the profit per dollar long of the weighted strategy.

        Each share's weight is its past return minus the cross-sectional
        average, scaled so that the long side sums to one.

        Args:
            previous: Past half-year returns by share.
            current: The following half-year's returns by share.

        Returns:
            The profit, NaN when fewer than 20 shares have both returns.

        Raises:
            None.
        """
        both = pd.concat([previous, current], axis=1).dropna()
        if len(both) < 20:
            return float('nan')
        deviations = both.iloc[:, 0] - both.iloc[:, 0].mean()
        scale = deviations[deviations > 0].sum()
        return float((deviations / scale * both.iloc[:, 1]).sum())

    def wrss_series(self, half_years: pd.DataFrame) -> pd.Series:
        """Gives the weighted strategy's profit in every half-year.

        Args:
            half_years: Half-year returns from half_year_returns.

        Returns:
            Profits indexed by the half-year they were earned in.

        Raises:
            None.
        """
        values = {}
        for position in range(1, len(half_years)):
            label = half_years.index[position]
            values[label] = self.wrss_profit(
                half_years.iloc[position - 1],
                half_years.iloc[position],
            )
        return pd.Series(values)

    def serial_covariance(self, series: pd.Series) -> float:
        """Gives the first-order serial covariance of a series.

        Args:
            series: The series.

        Returns:
            The sample covariance of the series with its lag.

        Raises:
            None.
        """
        pairs = pd.concat([series, series.shift(1)], axis=1).dropna()
        return float(pairs.iloc[:, 0].cov(pairs.iloc[:, 1]))

    def residual_serial_covariance(self, half_years: pd.DataFrame) -> float:
        """Averages the serial covariance of market-model residuals.

        Each share's half-year returns are regressed on the equally weighted
        average of all shares' half-year returns. Shares need 16 half-years.

        Args:
            half_years: Half-year returns, half-years by shares.

        Returns:
            The average over shares of the covariance of the residual with
            its lag.

        Raises:
            None.
        """
        index_returns = half_years.mean(axis=1)
        covariances = []
        for symbol in half_years.columns:
            joined = pd.concat([half_years[symbol], index_returns], axis=1)
            joined = joined.dropna()
            if len(joined) < 16:
                continue
            explanatory = statsmodels_api.add_constant(joined.iloc[:, 1])
            fitted = statsmodels_api.OLS(joined.iloc[:, 0], explanatory).fit()
            residuals = fitted.resid
            covariances.append(self.serial_covariance(residuals))
        return float(np.mean(covariances))

    def lead_lag(
        self,
        cohort_returns: pd.Series,
        market_monthly: pd.Series,
        first: pd.Period,
        last: pd.Period,
    ) -> dict[str, float]:
        """Regresses cohort profits on the squared past market return.

        The dependent variable is the six-month winners-minus-losers return
        of the cohort formed at the end of each month. The explanatory
        variable is the squared demeaned market return over the six months
        up to formation. The standard errors are Newey-West with six lags.

        Args:
            cohort_returns: Six-month cohort returns by formation month.
            market_monthly: The market's monthly returns.
            first: The first formation month.
            last: The last formation month.

        Returns:
            A dictionary with theta, theta_t and observations.

        Raises:
            None.
        """
        market_logs = np.log1p(market_monthly)
        past = np.expm1(market_logs.rolling(6, min_periods=6).sum())
        window = past.loc[first:last]
        squared = (window - window.mean()) ** 2
        joined = pd.concat([cohort_returns, squared], axis=1).dropna()
        joined = joined.loc[first:last]
        explanatory = statsmodels_api.add_constant(joined.iloc[:, 1])
        fitted = statsmodels_api.OLS(joined.iloc[:, 0], explanatory).fit(
            cov_type='HAC',
            cov_kwds={'maxlags': 6},
        )
        return {
            'theta': float(fitted.params.iloc[1]),
            'theta_t': float(fitted.tvalues.iloc[1]),
            'observations': float(len(joined)),
        }

    def table(
        self,
        standard_returns: pd.DataFrame,
        eligible: pd.DataFrame,
        deciles: pd.DataFrame,
        market_monthly: pd.Series,
    ) -> pd.DataFrame:
        """Computes every Section III quantity for one universe.

        Args:
            standard_returns: Monthly returns, months by shares.
            eligible: Bools, months by shares, for the universe.
            deciles: Six-month ranking deciles for the universe.
            market_monthly: The NIFTY 500 total return by month.

        Returns:
            Rows with columns quantity, value and t.

        Raises:
            None.
        """
        first = StudySettings.MAIN_FIRST
        last = StudySettings.MAIN_LAST
        half = self.half_year_returns(standard_returns, eligible)
        half_main = half.loc[first - 1 : last]
        profits = self.wrss_series(half_main).loc[first:last]
        mean, t_statistic = self.statistics.mean_and_t(profits)
        index_returns = half_main.mean(axis=1)
        cohort = EventTimeReturns(deciles, standard_returns, 6)
        decile_profit = cohort.holding_period_return(6)
        shifted = decile_profit.copy()
        shifted.index = shifted.index + 6
        aligned = pd.concat([profits, shifted], axis=1).dropna()
        rows = [
            {
                'quantity': 'WRSS profit per dollar long per half-year',
                'value': mean,
                't': t_statistic,
            },
            {
                'quantity': 'half-years in WRSS sample',
                'value': float(len(profits.dropna())),
                't': float('nan'),
            },
            {
                'quantity': 'correlation of WRSS with 6/6 decile strategy',
                'value': float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1])),
                't': float('nan'),
            },
            {
                'quantity': 'serial covariance of half-year equal-weight index',
                'value': self.serial_covariance(index_returns),
                't': float('nan'),
            },
            {
                'quantity': 'average serial covariance of residuals',
                'value': self.residual_serial_covariance(half_main),
                't': float('nan'),
            },
        ]
        middle = first + (last - first).n // 2
        windows = {
            'all': (first - 1, last - 6),
            'first half': (first - 1, middle),
            'second half': (middle + 1, last - 6),
        }
        for name, (begin, end) in windows.items():
            result = self.lead_lag(decile_profit, market_monthly, begin, end)
            rows.append(
                {
                    'quantity': f'lead-lag theta, {name}',
                    'value': result['theta'],
                    't': result['theta_t'],
                }
            )
        return pd.DataFrame(rows)
