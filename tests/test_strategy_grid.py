"""An end-to-end test of the strategy grid on made-up returns."""

import types

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.strategy_grid import StrategyGrid


class TestStrategyGrid:
    """Checks that persistent returns give positive momentum profits."""

    def _inputs(self) -> types.SimpleNamespace:
        """Makes returns where each share has its own steady drift.

        Args:
            None.

        Returns:
            An object with the attributes the grid reads.

        Raises:
            None.
        """
        generator = np.random.default_rng(7)
        months = pd.period_range('2004-01', '2026-09', freq='M')
        names = [f'S{number}' for number in range(150)]
        drift = generator.normal(0.01, 0.02, len(names))
        noise = generator.normal(0.0, 0.04, (len(months), len(names)))
        returns = pd.DataFrame(drift + noise, index=months, columns=names)
        mask = pd.DataFrame(True, index=months, columns=names)
        market = pd.Series(
            generator.normal(0.01, 0.04, len(months)),
            index=months,
        )
        return types.SimpleNamespace(
            standard_returns=returns,
            shifted_returns=returns.copy(),
            universe_a=mask,
            universe_b=mask,
            market_monthly=market,
        )

    def test_grid_runs_all_strategies_with_positive_spreads(self) -> None:
        """Checks 64 rows, positive spreads and costs below gross returns.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the grid is wrong.
        """
        grid = StrategyGrid(self._inputs())
        table = grid.run()
        assert len(table) == 64
        assert (table['bs_mean'] > 0).all()
        assert (table['bs_net_mean'] < table['bs_mean']).all()
        assert (table['buy_mean'] > table['sell_mean']).all()
        assert table['bs_months'].iloc[0] == 237
        assert 'A_noskip_6_6_bs_net' in grid.series
