"""Chooses which shares can be ranked each month."""

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.market_panels import MarketPanels


class UniverseBuilder:
    """Builds universe A (every share) and universe B (the liquid 500).

    Attributes:
        panels: The daily panels.
        window_sessions: Sessions used to measure liquidity, about a year.
        top_count: How many shares universe B keeps.
        minimum_trading_share: The share of sessions in the window on which a
            share must have traded to be in universe B.
        recent_sessions: Sessions at the month end in which a universe A
            share must have traded.
    """

    def __init__(
        self,
        panels: MarketPanels,
        window_sessions: int = 250,
        top_count: int = 500,
        minimum_trading_share: float = 0.8,
        recent_sessions: int = 5,
    ) -> None:
        """Sets the rules.

        Args:
            panels: The daily panels.
            window_sessions: Sessions used to measure liquidity.
            top_count: How many shares universe B keeps.
            minimum_trading_share: The share of sessions a share must trade.
            recent_sessions: Sessions at the month end a share must trade in.

        Returns:
            None.

        Raises:
            None.
        """
        self.panels = panels
        self.window_sessions = window_sessions
        self.top_count = top_count
        self.minimum_trading_share = minimum_trading_share
        self.recent_sessions = recent_sessions

    def universe_a(self, monthly_returns: pd.DataFrame) -> pd.DataFrame:
        """Gives every share with a return this month that traded recently.

        Args:
            monthly_returns: Standard monthly returns, months by shares.

        Returns:
            Bools, months by shares.

        Raises:
            None.
        """
        recent = self.panels.traded_in_last_sessions(self.recent_sessions)
        recent = recent.reindex(
            index=monthly_returns.index,
            columns=monthly_returns.columns,
            fill_value=False,
        )
        return recent & monthly_returns.notna()

    def liquidity(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Measures each share's trading over the window before each month end.

        A session without a trade counts as a traded value of zero, so the
        median is low for a share that trades rarely.

        Args:
            None.

        Returns:
            A pair of tables, months by shares: the median daily traded value
            in rupees and the share of sessions traded. Months with fewer
            than window_sessions sessions of history are NaN.

        Raises:
            None.
        """
        positions = self.panels.month_end_positions()
        values = self.panels.traded_values.to_numpy()
        medians = np.full((len(positions), values.shape[1]), np.nan)
        shares = np.full((len(positions), values.shape[1]), np.nan)
        for row, position in enumerate(positions.to_numpy()):
            first = position - self.window_sessions + 1
            if first < 0:
                continue
            window = values[first : position + 1]
            traded = ~np.isnan(window)
            medians[row] = np.median(np.nan_to_num(window), axis=0)
            shares[row] = traded.mean(axis=0)
        columns = self.panels.traded_values.columns
        return (
            pd.DataFrame(medians, index=positions.index, columns=columns),
            pd.DataFrame(shares, index=positions.index, columns=columns),
        )

    def universe_b(
        self,
        universe_a: pd.DataFrame,
        median_values: pd.DataFrame,
        trading_shares: pd.DataFrame,
    ) -> pd.DataFrame:
        """Keeps the most traded shares of universe A.

        Args:
            universe_a: Universe A, months by shares.
            median_values: Median daily traded values from liquidity.
            trading_shares: Share of sessions traded from liquidity.

        Returns:
            Bools, months by shares, with at most top_count True per month.

        Raises:
            None.
        """
        candidates = universe_a & (trading_shares >= self.minimum_trading_share)
        ranked = median_values.where(candidates)
        order = ranked.rank(axis=1, ascending=False, method='first')
        return candidates & (order <= self.top_count)
