"""Tests for universes A and B."""

import pandas as pd
from panel_fixtures import PanelFixtures

from jegadeesh_titman_india.momentum.market_panels import MarketPanels
from jegadeesh_titman_india.momentum.universes import UniverseBuilder


class TestUniverseBuilder:
    """Checks on who is eligible each month."""

    def _builder(self, top_count: int = 1) -> UniverseBuilder:
        """Makes a builder with a four-session liquidity window.

        Args:
            top_count: How many shares universe B keeps.

        Returns:
            The builder.

        Raises:
            None.
        """
        panels = MarketPanels(
            PanelFixtures().daily(),
            last_month=pd.Period('2020-03'),
            skip_sessions=1,
        )
        return UniverseBuilder(
            panels,
            window_sessions=4,
            top_count=top_count,
            minimum_trading_share=0.8,
            recent_sessions=2,
        )

    def test_universe_a_needs_a_return_and_a_recent_trade(self) -> None:
        """Checks that C leaves universe A in March.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the flags are wrong.
        """
        builder = self._builder()
        monthly = builder.panels.standard_returns()
        universe = builder.universe_a(monthly)
        assert universe.loc[pd.Period('2020-02')].all()
        assert not universe.loc[pd.Period('2020-03'), 'C']

    def test_liquidity_counts_missing_sessions_as_zero(self) -> None:
        """Checks the median value and trading share of share C in March.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the measures are wrong.
        """
        builder = self._builder()
        medians, shares = builder.liquidity()
        assert medians.loc[pd.Period('2020-02'), 'C'] == 10.0
        assert medians.loc[pd.Period('2020-03'), 'C'] == 0.0
        assert shares.loc[pd.Period('2020-03'), 'C'] == 0.25
        assert medians.loc[pd.Period('2020-01')].isna().all()

    def test_universe_b_keeps_the_most_traded(self) -> None:
        """Checks that only share A, the most traded, is kept.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When universe B is wrong.
        """
        builder = self._builder(top_count=1)
        monthly = builder.panels.standard_returns()
        universe_a = builder.universe_a(monthly)
        medians, shares = builder.liquidity()
        universe_b = builder.universe_b(universe_a, medians, shares)
        assert list(universe_b.loc[pd.Period('2020-02')]) == [
            True,
            False,
            False,
        ]
