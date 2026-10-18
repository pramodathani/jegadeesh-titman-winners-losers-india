"""Tests for event-time returns."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.event_time import (
    EventTimeReturns,
    EventTimeSummary,
)


class TestEventTimeReturns:
    """Checks on winners-minus-losers returns after formation."""

    def _event(self) -> EventTimeReturns:
        """Makes four months and four shares with known returns.

        Args:
            None.

        Returns:
            The event-time object with a horizon of two months.

        Raises:
            None.
        """
        months = pd.period_range('2020-01', periods=4, freq='M')
        columns = list('ABCD')
        deciles = pd.DataFrame(
            np.nan,
            index=months,
            columns=columns,
        )
        deciles.iloc[0] = [10, 10, 1, 5]
        deciles.iloc[1] = [1, 10, 10, 5]
        returns = pd.DataFrame(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.10, 0.20, -0.10, 0.0],
                [0.00, 0.10, 0.30, 0.0],
                [0.05, 0.05, 0.05, 0.0],
            ],
            index=months,
            columns=columns,
        )
        return EventTimeReturns(deciles, returns, horizon=2)

    def test_first_event_month_is_the_month_after_formation(self) -> None:
        """Checks January's winners and losers in February.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        zero_cost = self._event().zero_cost()
        january = zero_cost.loc[pd.Period('2020-01')]
        assert math.isclose(january[1], 0.15 - -0.10)
        assert math.isclose(january[2], 0.05 - 0.30)

    def test_late_formations_lack_later_months(self) -> None:
        """Checks that a month near the end has NaN beyond the data.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the value is present.
        """
        zero_cost = self._event().zero_cost()
        assert math.isnan(zero_cost.loc[pd.Period('2020-03'), 1])

    def test_holding_period_return_compounds(self) -> None:
        """Checks the two-month compounded winners-minus-losers return.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the value is wrong.
        """
        result = self._event().holding_period_return(2)
        winners = 1.15 * 1.05 - 1.0
        losers = 0.90 * 1.30 - 1.0
        assert math.isclose(result.loc[pd.Period('2020-01')], winners - losers)

    def test_summary_averages_over_formation_months(self) -> None:
        """Checks the cumulative average over two formations.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the summary is wrong.
        """
        zero_cost = pd.DataFrame(
            {1: [0.01, 0.03, 0.02, 0.04], 2: [0.02, 0.0, 0.01, 0.01]},
            index=pd.period_range('2020-01', periods=4, freq='M'),
        )
        summary = EventTimeSummary().summarize(
            zero_cost,
            pd.Period('2020-01'),
            pd.Period('2020-04'),
        )
        assert math.isclose(summary.loc[0, 'monthly'], 0.025)
        assert math.isclose(summary.loc[1, 'cumulative'], 0.025 + 0.01)
        assert summary.loc[0, 'formations'] == 4
