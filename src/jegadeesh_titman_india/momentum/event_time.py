"""Returns of decile portfolios in the months after formation."""

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics


class EventTimeReturns:
    """Average returns of winners and losers in event months 1 to H.

    Attributes:
        deciles: Decile numbers at the end of each month.
        returns: Monthly returns, months by shares.
        horizon: H, the number of event months.
    """

    def __init__(
        self,
        deciles: pd.DataFrame,
        returns: pd.DataFrame,
        horizon: int = 36,
    ) -> None:
        """Keeps the inputs, aligned.

        Args:
            deciles: Decile numbers at the end of each month.
            returns: Monthly returns used for the event months.
            horizon: The number of event months.

        Returns:
            None.

        Raises:
            None.
        """
        self.deciles = deciles
        self.returns = returns.reindex(
            index=deciles.index,
            columns=deciles.columns,
        )
        self.horizon = horizon

    def leg(self, decile: int) -> pd.DataFrame:
        """Gives the equally weighted return of one decile in each event month.

        Args:
            decile: The decile.

        Returns:
            A table with one row per formation month and columns 1 to H.

        Raises:
            None.
        """
        members = self.deciles == decile
        columns = {}
        for month_ahead in range(1, self.horizon + 1):
            later = self.returns.shift(-month_ahead)
            columns[month_ahead] = later.where(members).mean(axis=1)
        return pd.DataFrame(columns)

    def zero_cost(self) -> pd.DataFrame:
        """Gives the winners-minus-losers return in each event month.

        Args:
            None.

        Returns:
            A table with one row per formation month and columns 1 to H.

        Raises:
            None.
        """
        return self.leg(10) - self.leg(1)

    def holding_period_return(
        self,
        months: int,
    ) -> pd.Series:
        """Gives the compounded winners-minus-losers return over K months.

        Args:
            months: How many event months to compound.

        Returns:
            One value per formation month.

        Raises:
            None.
        """
        winners = (1.0 + self.leg(10).iloc[:, :months]).prod(
            axis=1, min_count=months
        )
        losers = (1.0 + self.leg(1).iloc[:, :months]).prod(
            axis=1, min_count=months
        )
        return winners - losers


class EventTimeSummary:
    """Averages event-time returns over formation months, as in Table VII."""

    def summarize(
        self,
        zero_cost: pd.DataFrame,
        first_formation: pd.Period,
        last_formation: pd.Period,
    ) -> pd.DataFrame:
        """Averages monthly and cumulative returns with t-statistics.

        The monthly t-statistic is ordinary. The cumulative return is the
        running sum of the monthly averages, and its t-statistic is
        Newey-West with as many lags as event months, because the
        cumulative returns of neighbouring formation months overlap.

        Args:
            zero_cost: The table from EventTimeReturns.zero_cost.
            first_formation: The first formation month used.
            last_formation: The last formation month used.

        Returns:
            One row per event month with columns month, monthly, monthly_t,
            cumulative, cumulative_t and formations.

        Raises:
            None.
        """
        window = zero_cost.loc[first_formation:last_formation]
        statistics = ReturnStatistics()
        cumulative = window.cumsum(axis=1)
        rows = []
        for month_ahead in window.columns:
            monthly, monthly_t = statistics.mean_and_t(window[month_ahead])
            running, running_t = statistics.newey_west_mean_and_t(
                cumulative[month_ahead],
                lags=int(month_ahead),
            )
            rows.append(
                {
                    'month': month_ahead,
                    'monthly': monthly,
                    'monthly_t': monthly_t,
                    'cumulative': running,
                    'cumulative_t': running_t,
                    'formations': int(window[month_ahead].notna().sum()),
                }
            )
        return pd.DataFrame(rows)
