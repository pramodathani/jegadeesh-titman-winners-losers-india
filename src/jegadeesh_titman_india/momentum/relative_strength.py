"""The Jegadeesh and Titman relative strength strategy on monthly data."""

import pandas as pd
from brahmagupta.backtest import Backtest
from brahmagupta.costs.cost_model import CostModel
from brahmagupta.overlapping_cohorts import OverlappingCohorts


class RelativeStrengthStrategy:
    """Overlapping decile portfolios held for K months.

    Attributes:
        deciles: Decile numbers at the end of each month, months by shares.
        holding_months: K, how long each cohort is held.
        holding_returns: The returns earned in each holding month.
    """

    def __init__(
        self,
        deciles: pd.DataFrame,
        holding_months: int,
        holding_returns: pd.DataFrame,
    ) -> None:
        """Lines up the returns with the deciles.

        Args:
            deciles: Decile numbers at the end of each month.
            holding_months: K.
            holding_returns: Returns in each holding month; the row for month
                t is earned by cohorts formed at the end of earlier months.

        Returns:
            None.

        Raises:
            None.
        """
        self.deciles = deciles
        self.holding_months = holding_months
        self.holding_returns = holding_returns.reindex(
            index=deciles.index,
            columns=deciles.columns,
        )

    def weights(self, decile: int) -> pd.DataFrame:
        """Gives the weights of the portfolio that holds one decile.

        Args:
            decile: The decile, 1 for losers and 10 for winners.

        Returns:
            Weights at the start of each month, summing to 1 when held.

        Raises:
            None.
        """
        members = self.deciles == decile
        formed = self.deciles.notna().any(axis=1)
        cohorts = OverlappingCohorts(members, self.holding_months, formed)
        return cohorts.weights(self.holding_returns)

    def long_short_weights(
        self,
        buy_decile: int = 10,
        sell_decile: int = 1,
    ) -> pd.DataFrame:
        """Gives the weights that buy one decile and sell another.

        Args:
            buy_decile: The decile bought.
            sell_decile: The decile sold.

        Returns:
            Weights, with the bought side summing to 1 and the sold side to
            minus 1 when held.

        Raises:
            None.
        """
        return self.weights(buy_decile) - self.weights(sell_decile)

    def run(
        self,
        weights: pd.DataFrame,
        cost_model: CostModel | None,
    ) -> pd.DataFrame:
        """Runs weights through brahmagupta's backtest.

        Args:
            weights: Target weights, months by shares.
            cost_model: The cost model, or None for no costs.

        Returns:
            A table with columns gross_return, bought, sold, turnover, costs,
            net_return, unpriced_weight and holding_count, one row per month.

        Raises:
            None.
        """
        backtest = Backtest(self.holding_returns, weights, cost_model)
        return backtest.run().to_frame()
