"""Session-by-share panels and the monthly returns made from them."""

import numpy as np
import pandas as pd


class MarketPanels:
    """Daily panels of returns and traded values, and monthly returns.

    Attributes:
        sessions: The trading dates, sorted.
        daily_returns: Returns, sessions by shares, NaN where no trade.
        traded_values: Traded value in rupees, sessions by shares.
        skip_sessions: Sessions between ranking and holding in Panel B.
    """

    def __init__(
        self,
        daily: pd.DataFrame,
        last_month: pd.Period,
        skip_sessions: int = 5,
    ) -> None:
        """Builds the panels from the long daily table.

        Args:
            daily: Columns date, symbol, traded_value and ret.
            last_month: The last complete month; later months are not reported
            but their sessions complete the final skip period.
            skip_sessions: Sessions between ranking and holding in Panel B.

        Returns:
            None.

        Raises:
            None.
        """
        self.last_month = last_month
        self.skip_sessions = skip_sessions
        self.daily_returns = daily.pivot(
            index='date',
            columns='symbol',
            values='ret',
        )
        self.traded_values = daily.pivot(
            index='date',
            columns='symbol',
            values='traded_value',
        ).astype('float32')
        self.traded_values = self.traded_values.reindex(
            self.daily_returns.index
        )
        self.daily_returns = self.daily_returns.reindex(
            columns=self.traded_values.columns
        )
        self.sessions = self.daily_returns.index
        self._traded = self.traded_values.notna()

    def month_end_positions(self) -> pd.Series:
        """Gives the position of each month's last session.

        Args:
            None.

        Returns:
            A series indexed by month holding the session position.

        Raises:
            None.
        """
        months = self.sessions.to_period('M')
        positions = pd.Series(np.arange(len(self.sessions)), index=months)
        positions = positions.groupby(level=0).max()
        return positions[positions.index <= self.last_month]

    def traded_in_last_sessions(self, count: int) -> pd.DataFrame:
        """Says whether each share traded in the last sessions of each month.

        Args:
            count: How many final sessions of the month to look at.

        Returns:
            Bools, months by shares.

        Raises:
            None.
        """
        positions = self.month_end_positions()
        values = np.zeros((len(positions), self._traded.shape[1]), dtype=bool)
        traded = self._traded.to_numpy()
        for row, position in enumerate(positions.to_numpy()):
            first = max(0, position - count + 1)
            values[row] = traded[first : position + 1].any(axis=0)
        return pd.DataFrame(
            values,
            index=positions.index,
            columns=self._traded.columns,
        )

    def standard_returns(self) -> pd.DataFrame:
        """Compounds daily returns within each calendar month.

        Args:
            None.

        Returns:
            Returns, months by shares, NaN where a share had no return.

        Raises:
            None.
        """
        logs = np.log1p(self.daily_returns)
        months = self.sessions.to_period('M')
        grouped = logs.groupby(months).sum(min_count=1)
        grouped = grouped[grouped.index <= self.last_month]
        return np.expm1(grouped)

    def shifted_returns(self) -> pd.DataFrame:
        """Compounds daily returns over months that start after the skip.

        The month labelled m runs from the session after the skip that
        follows the last session of the month before m, up to the skip
        session after the last session of month m. A cohort ranked at the
        end of the month before m therefore starts holding skip_sessions
        sessions after its ranking.

        Args:
            None.

        Returns:
            Returns, months by shares, NaN where a share had no return.

        Raises:
            None.
        """
        positions = self.month_end_positions()
        boundaries = positions.to_numpy() + self.skip_sessions
        months = positions.index
        session_positions = np.arange(len(self.sessions))
        passed = np.searchsorted(boundaries, session_positions, side='left')
        valid = passed > 0
        labels = months[passed[valid] - 1] + 1
        logs = np.log1p(self.daily_returns.iloc[np.flatnonzero(valid)])
        grouped = logs.groupby(np.asarray(labels)).sum(min_count=1)
        grouped.index = pd.PeriodIndex(grouped.index, freq='M')
        grouped = grouped[grouped.index <= self.last_month]
        return np.expm1(grouped)
