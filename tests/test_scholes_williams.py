"""Tests for Scholes-Williams betas."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.scholes_williams import (
    ScholesWilliamsBetas,
)


class TestScholesWilliamsBetas:
    """Checks on beta estimates."""

    def _market(self) -> pd.Series:
        """Makes 200 random market returns in 2020.

        Args:
            None.

        Returns:
            The market return series.

        Raises:
            None.
        """
        generator = np.random.default_rng(1)
        dates = pd.bdate_range('2020-01-01', periods=200)
        return pd.Series(generator.normal(0, 0.01, 200), index=dates)

    def test_share_that_moves_twice_the_market_has_beta_two(self) -> None:
        """Checks a share that is exactly twice the market.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the beta is not near two.
        """
        market = self._market()
        shares = pd.DataFrame({'A': 2.0 * market})
        betas = ScholesWilliamsBetas().estimate(shares, market)
        assert math.isclose(betas.loc[2020, 'A'], 2.0, rel_tol=0.1)

    def test_too_few_days_gives_nan(self) -> None:
        """Checks that a share with few returns has no beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a beta is given.
        """
        market = self._market()
        sparse = (2.0 * market).copy()
        sparse.iloc[:150] = np.nan
        betas = ScholesWilliamsBetas().estimate(
            pd.DataFrame({'A': sparse}),
            market,
        )
        assert math.isnan(betas.loc[2020, 'A'])

    def test_lagged_reaction_is_captured(self) -> None:
        """Checks that a share reacting a day late still gets beta near one.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the beta is far from one.
        """
        market = self._market()
        late = market.shift(1).fillna(0.0)
        betas = ScholesWilliamsBetas().estimate(
            pd.DataFrame({'A': late}),
            market,
        )
        assert math.isclose(betas.loc[2020, 'A'], 1.0, rel_tol=0.2)
