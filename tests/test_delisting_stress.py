"""Tests for the delisting stress."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.delisting_stress import DelistingStress


class TestDelistingStress:
    """Checks on where the loss is inserted."""

    def _returns(self) -> pd.DataFrame:
        """Makes six months for three shares.

        Share A stops after March, B trades throughout, and C stops in the
        last month, which is too recent to call an exit.

        Args:
            None.

        Returns:
            The returns.

        Raises:
            None.
        """
        months = pd.period_range('2020-01', periods=6, freq='M')
        returns = pd.DataFrame(0.01, index=months, columns=list('ABC'))
        returns.loc[months[3:], 'A'] = np.nan
        returns.loc[months[5], 'C'] = np.nan
        return returns

    def test_loss_goes_in_the_month_after_the_last_return(self) -> None:
        """Checks A loses 100 percent in April and nothing else changes.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the loss is misplaced.
        """
        stressed = DelistingStress().stressed_returns(self._returns())
        assert stressed.loc[pd.Period('2020-04'), 'A'] == -1.0
        assert math.isnan(stressed.loc[pd.Period('2020-05'), 'A'])
        assert math.isnan(stressed.loc[pd.Period('2020-06'), 'C'])
        assert stressed['B'].eq(0.01).all()

    def test_original_returns_are_not_changed(self) -> None:
        """Checks that the input table is left alone.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the input changes.
        """
        returns = self._returns()
        before = returns.copy()
        DelistingStress().stressed_returns(returns)
        assert returns.equals(before)
