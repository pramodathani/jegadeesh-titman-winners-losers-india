"""Ranks shares on their past returns and splits them into deciles."""

import numpy as np
import pandas as pd


class PastReturnRanker:
    """Computes J-month past returns and decile numbers.

    Attributes:
        ranking_months: J, the number of months of past returns.
        minimum_shares: The fewest ranked shares for a month to form deciles.
    """

    def __init__(
        self,
        ranking_months: int,
        minimum_shares: int = 100,
    ) -> None:
        """Sets J and the smallest cross-section.

        Args:
            ranking_months: J, the number of months of past returns.
            minimum_shares: The fewest ranked shares for a month to count.

        Returns:
            None.

        Raises:
            ValueError: When ranking_months is less than 1.
        """
        if ranking_months < 1:
            raise ValueError('ranking_months must be at least 1')
        self.ranking_months = ranking_months
        self.minimum_shares = minimum_shares

    def past_returns(self, monthly_returns: pd.DataFrame) -> pd.DataFrame:
        """Compounds the last J monthly returns, needing all J to be present.

        Args:
            monthly_returns: Standard monthly returns, months by shares.

        Returns:
            Past returns, months by shares, NaN where any of the J months has
            no return. The value in month t uses months t-J+1 to t.

        Raises:
            None.
        """
        logs = np.log1p(monthly_returns)
        window = logs.rolling(
            self.ranking_months,
            min_periods=self.ranking_months,
        ).sum()
        return np.expm1(window)

    def deciles(
        self,
        past_returns: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> pd.DataFrame:
        """Numbers the eligible shares from 1 (losers) to 10 (winners).

        Shares are ranked by past return within each month. Ties are broken
        by column order, and decile sizes differ by at most one share.

        Args:
            past_returns: Past returns, months by shares.
            eligible: Bools, months by shares, for the universe.

        Returns:
            Decile numbers, months by shares, NaN where a share is not
            ranked or the month has fewer than minimum_shares ranked shares.

        Raises:
            None.
        """
        usable = past_returns.where(eligible.reindex_like(past_returns))
        ranks = usable.rank(axis=1, method='first', ascending=True)
        counts = usable.notna().sum(axis=1)
        deciles = np.floor((ranks - 1.0).div(counts, axis=0) * 10.0) + 1.0
        too_few = counts < self.minimum_shares
        deciles[too_few.to_numpy()] = np.nan
        return deciles
