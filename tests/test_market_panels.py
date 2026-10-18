"""Tests for monthly returns from daily panels."""

import math

import pandas as pd
from panel_fixtures import PanelFixtures

from jegadeesh_titman_india.momentum.market_panels import MarketPanels


class TestMarketPanels:
    """Checks on standard and shifted monthly returns."""

    def _panels(self) -> MarketPanels:
        """Makes panels for the fixture, with a skip of one session.

        Args:
            None.

        Returns:
            The panels, with March 2020 as the last month.

        Raises:
            None.
        """
        return MarketPanels(
            PanelFixtures().daily(),
            last_month=pd.Period('2020-03'),
            skip_sessions=1,
        )

    def test_standard_month_compounds_daily_returns(self) -> None:
        """Checks February for share A: sessions 3, 4 and 5.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the month's return is wrong.
        """
        monthly = self._panels().standard_returns()
        expected = 1.04 * 1.05 * 1.06 - 1.0
        assert math.isclose(monthly.loc[pd.Period('2020-02'), 'A'], expected)
        assert pd.Period('2020-04') not in monthly.index

    def test_missing_share_has_no_return(self) -> None:
        """Checks that share C has no March return.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is present.
        """
        monthly = self._panels().standard_returns()
        assert math.isnan(monthly.loc[pd.Period('2020-03'), 'C'])

    def test_shifted_month_starts_after_the_skip(self) -> None:
        """Checks that February runs from session 4 to the skip after it.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the shifted returns are wrong.
        """
        shifted = self._panels().shifted_returns()
        february = 1.05 * 1.06 * 1.07 - 1.0
        march = 1.08 * 1.09 * 1.10 - 1.0
        assert math.isclose(shifted.loc[pd.Period('2020-02'), 'A'], february)
        assert math.isclose(shifted.loc[pd.Period('2020-03'), 'A'], march)
        assert pd.Period('2020-01') not in shifted.index
        assert pd.Period('2020-04') not in shifted.index

    def test_traded_in_last_sessions(self) -> None:
        """Checks the recent trading flag for shares A and C.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the flags are wrong.
        """
        flags = self._panels().traded_in_last_sessions(2)
        assert flags.loc[pd.Period('2020-02'), 'C']
        assert not flags.loc[pd.Period('2020-03'), 'C']
        assert flags.loc[pd.Period('2020-03'), 'A']

    def test_earlier_month_ends_before_the_month_end(self) -> None:
        """Checks that each month ends one session before its last session.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the earlier returns are wrong.
        """
        earlier = self._panels().earlier_returns()
        january = 1.01 * 1.02 - 1.0
        february = 1.03 * 1.04 * 1.05 - 1.0
        march = 1.06 * 1.07 * 1.08 - 1.0
        assert math.isclose(earlier.loc[pd.Period('2020-01'), 'A'], january)
        assert math.isclose(earlier.loc[pd.Period('2020-02'), 'A'], february)
        assert math.isclose(earlier.loc[pd.Period('2020-03'), 'A'], march)
        assert pd.Period('2020-04') not in earlier.index
