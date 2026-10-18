"""Table IX: returns around earnings announcements of winners and losers."""

import numpy as np
import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics


class EarningsTable:
    """Three-day announcement returns by months since ranking.

    Attributes:
        market_close: Minutes after midnight at which NSE's session ends.
        horizon: How many months after ranking are tracked.
    """

    def __init__(self, horizon: int = 36) -> None:
        """Sets the horizon.

        Args:
            horizon: How many months after ranking are tracked.

        Returns:
            None.

        Raises:
            None.
        """
        self.market_close = 15 * 60 + 30
        self.horizon = horizon

    def event_positions(
        self,
        announced: pd.Series,
        sessions: pd.DatetimeIndex,
    ) -> np.ndarray:
        """Finds the session on which each announcement can first matter.

        That is the announcement date when it is a session and the time is
        within trading hours, otherwise the next session.

        Args:
            announced: Announcement times.
            sessions: The trading dates, sorted.

        Returns:
            Session positions, with -1 when no session is found.

        Raises:
            None.
        """
        dates = announced.dt.normalize().to_numpy()
        positions = np.searchsorted(sessions.to_numpy(), dates, side='left')
        minutes = announced.dt.hour * 60 + announced.dt.minute
        after_hours = (minutes > self.market_close).to_numpy()
        is_session = np.zeros(len(positions), dtype=bool)
        inside = positions < len(sessions)
        is_session[inside] = (
            sessions.to_numpy()[positions[inside]] == dates[inside]
        )
        positions = np.where(is_session & after_hours, positions + 1, positions)
        positions = np.where(positions >= len(sessions), -1, positions)
        return positions

    def window_returns(
        self,
        daily_returns: pd.DataFrame,
        announcements: pd.DataFrame,
        positions: np.ndarray,
    ) -> np.ndarray:
        """Compounds each announcement's returns on days -2, -1 and 0.

        Args:
            daily_returns: Returns, sessions by shares.
            announcements: Rows with a symbol column.
            positions: Day-0 session position of each announcement.

        Returns:
            One three-day return per announcement, NaN when the share has no
            symbol in the panel or traded on fewer than two of the days.

        Raises:
            None.
        """
        values = daily_returns.to_numpy()
        columns = daily_returns.columns.get_indexer(announcements['symbol'])
        result = np.full(len(announcements), np.nan)
        for offset in range(len(announcements)):
            position = positions[offset]
            column = columns[offset]
            if position < 2 or column < 0:
                continue
            window = values[position - 2 : position + 1, column]
            traded = ~np.isnan(window)
            if traded.sum() < 2:
                continue
            result[offset] = np.prod(1.0 + window[traded]) - 1.0
        return result

    def table(
        self,
        announcements: pd.DataFrame,
        daily_returns: pd.DataFrame,
        deciles: pd.DataFrame,
    ) -> pd.DataFrame:
        """Computes winners minus losers announcement returns by month t.

        Args:
            announcements: Columns symbol and announced.
            daily_returns: Returns, sessions by shares.
            deciles: Six-month ranking deciles, months by shares.

        Returns:
            One row per month t with the average difference, its t-statistic
            across formation months and counts of announcements.

        Raises:
            None.
        """
        announcements = announcements.reset_index(drop=True)
        positions = self.event_positions(
            announcements['announced'],
            daily_returns.index,
        )
        returns = self.window_returns(daily_returns, announcements, positions)
        month_index = announcements['announced'].dt.to_period('M')
        decile_values = deciles.to_numpy()
        decile_months = deciles.index
        columns = deciles.columns.get_indexer(announcements['symbol'])
        records = []
        for month_ahead in range(1, self.horizon + 1):
            formation = month_index - month_ahead
            rows = decile_months.get_indexer(formation)
            usable = (rows >= 0) & (columns >= 0) & ~np.isnan(returns)
            usable_rows = np.flatnonzero(usable)
            ranked = decile_values[rows[usable_rows], columns[usable_rows]]
            for position, decile in zip(usable_rows, ranked, strict=True):
                if decile == 10 or decile == 1:
                    records.append(
                        (
                            month_ahead,
                            rows[position],
                            decile == 10,
                            returns[position],
                        )
                    )
        frame = pd.DataFrame(
            records,
            columns=['t', 'formation', 'winner', 'ret'],
        )
        means = frame.groupby(['t', 'formation', 'winner'])['ret'].mean()
        wide = means.unstack('winner').dropna()
        difference = wide[True] - wide[False]
        counts = frame.groupby(['t', 'winner']).size().unstack('winner')
        statistics = ReturnStatistics()
        rows_out = []
        for month_ahead in range(1, self.horizon + 1):
            series = difference.xs(month_ahead, level='t')
            mean, t_statistic = statistics.mean_and_t(series)
            rows_out.append(
                {
                    't': month_ahead,
                    'winners_minus_losers': mean,
                    't_statistic': t_statistic,
                    'formation_months': len(series),
                    'winner_announcements': int(counts.loc[month_ahead, True]),
                    'loser_announcements': int(counts.loc[month_ahead, False]),
                }
            )
        return pd.DataFrame(rows_out)
