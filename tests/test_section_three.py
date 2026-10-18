"""Tests for the Section III calculations."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.section_three import SectionThree


class TestSectionThree:
    """Checks on the weighted relative strength strategy."""

    def test_wrss_profit_hand_computed(self) -> None:
        """Checks the profit per dollar long for four shares.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the profit is wrong.
        """
        names = [f'S{number}' for number in range(24)]
        previous = pd.Series([2.0, 1.0, -1.0, -2.0] + [0.0] * 20, index=names)
        current = pd.Series([0.2, 0.1, -0.1, -0.2] + [0.0] * 20, index=names)
        profit = SectionThree().wrss_profit(previous, current)
        assert math.isclose(profit, 1.0 / 3.0)

    def test_wrss_profit_needs_twenty_shares(self) -> None:
        """Checks that a thin cross-section gives NaN.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a profit is given.
        """
        previous = pd.Series([1.0, -1.0])
        current = pd.Series([1.0, -1.0])
        assert math.isnan(SectionThree().wrss_profit(previous, current))

    def test_half_year_returns_need_six_months(self) -> None:
        """Checks the June return compounds six months and needs all six.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        months = pd.period_range('2020-01', periods=12, freq='M')
        monthly = pd.DataFrame({'A': 0.01, 'B': 0.01}, index=months)
        monthly.loc[pd.Period('2020-03'), 'B'] = np.nan
        eligible = pd.DataFrame(True, index=months, columns=['A', 'B'])
        half = SectionThree().half_year_returns(monthly, eligible)
        assert list(half.index) == [pd.Period('2020-06'), pd.Period('2020-12')]
        assert math.isclose(half.loc[pd.Period('2020-06'), 'A'], 1.01**6 - 1.0)
        assert math.isnan(half.loc[pd.Period('2020-06'), 'B'])
        assert math.isclose(half.loc[pd.Period('2020-12'), 'B'], 1.01**6 - 1.0)

    def test_serial_covariance_of_alternating_series_is_negative(self) -> None:
        """Checks a series that alternates sign.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the covariance is not negative.
        """
        series = pd.Series([1.0, -1.0] * 10)
        assert SectionThree().serial_covariance(series) < 0
