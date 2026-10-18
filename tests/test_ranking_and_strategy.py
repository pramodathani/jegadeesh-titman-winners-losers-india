"""Tests for ranking, deciles and the overlapping decile portfolios."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.ranking import PastReturnRanker
from jegadeesh_titman_india.momentum.relative_strength import (
    RelativeStrengthStrategy,
)


class TestPastReturnRanker:
    """Checks on past returns and deciles."""

    def test_past_returns_use_only_the_last_j_months(self) -> None:
        """Checks a two-month past return and its NaN start.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the past returns are wrong.
        """
        months = pd.period_range('2020-01', periods=3, freq='M')
        monthly = pd.DataFrame({'A': [0.10, 0.20, -0.5]}, index=months)
        past = PastReturnRanker(2).past_returns(monthly)
        assert math.isnan(past['A'].iloc[0])
        assert math.isclose(past['A'].iloc[1], 1.1 * 1.2 - 1.0)
        assert math.isclose(past['A'].iloc[2], 1.2 * 0.5 - 1.0)

    def test_a_missing_month_makes_the_past_return_missing(self) -> None:
        """Checks that all J months must have a return.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the past return is present.
        """
        months = pd.period_range('2020-01', periods=3, freq='M')
        monthly = pd.DataFrame({'A': [0.1, np.nan, 0.1]}, index=months)
        past = PastReturnRanker(2).past_returns(monthly)
        assert past['A'].isna().all()

    def test_deciles_number_shares_from_losers_to_winners(self) -> None:
        """Checks ten shares fall one to a decile in order.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the deciles are wrong.
        """
        months = pd.period_range('2020-01', periods=1, freq='M')
        names = [f'S{number}' for number in range(10)]
        values = [0.5, -0.2, 0.1, 0.9, -0.9, 0.0, 0.3, 0.2, -0.1, 0.7]
        past = pd.DataFrame([values], index=months, columns=names)
        eligible = pd.DataFrame(True, index=months, columns=names)
        eligible.loc[months[0], 'S3'] = False
        result = PastReturnRanker(1, minimum_shares=5).deciles(past, eligible)
        assert math.isnan(result.loc[months[0], 'S3'])
        assert result.loc[months[0], 'S4'] == 1
        assert result.loc[months[0], 'S9'] == 9
        assert result.loc[months[0]].max() == 9

    def test_too_few_shares_gives_no_deciles(self) -> None:
        """Checks that a thin cross-section is left unranked.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When deciles are formed.
        """
        months = pd.period_range('2020-01', periods=1, freq='M')
        past = pd.DataFrame(
            [[0.1, 0.2, 0.3]], index=months, columns=list('ABC')
        )
        eligible = pd.DataFrame(True, index=months, columns=list('ABC'))
        result = PastReturnRanker(1, minimum_shares=5).deciles(past, eligible)
        assert result.isna().all().all()


class TestRelativeStrengthStrategy:
    """Checks on overlapping cohorts of decile portfolios."""

    def _strategy(self) -> RelativeStrengthStrategy:
        """Makes a three-month strategy on four shares with K equal to two.

        Args:
            None.

        Returns:
            The strategy.

        Raises:
            None.
        """
        months = pd.period_range('2020-01', periods=4, freq='M')
        columns = list('ABCD')
        deciles = pd.DataFrame(
            [
                [10, 1, 5, 5],
                [5, 5, 10, 1],
                [10, 1, 5, 5],
                [10, 1, 5, 5],
            ],
            index=months,
            columns=columns,
            dtype=float,
        )
        returns = pd.DataFrame(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.10, 0.00, 0.0, 0.0],
                [0.20, -0.10, 0.05, -0.05],
                [0.00, 0.00, 0.0, 0.0],
            ],
            index=months,
            columns=columns,
        )
        return RelativeStrengthStrategy(deciles, 2, returns)

    def test_winner_weights_split_across_cohorts(self) -> None:
        """Checks the March weights: the winners of January and of February.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the weights are wrong.
        """
        weights = self._strategy().weights(10)
        march = weights.loc[pd.Period('2020-03')]
        assert math.isclose(march['A'], 0.5)
        assert math.isclose(march['C'], 0.5)
        assert math.isclose(march.sum(), 1.0)
        assert weights.loc[pd.Period('2020-02')].sum() == 0.0

    def test_long_short_return_is_buy_minus_sell(self) -> None:
        """Checks the March return of the zero-cost portfolio.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        strategy = self._strategy()
        weights = strategy.long_short_weights()
        result = strategy.run(weights, None)
        march = result.loc[pd.Period('2020-03')]
        buy = 0.5 * 0.20 + 0.5 * 0.05
        sell = 0.5 * -0.10 + 0.5 * -0.05
        assert math.isclose(march['gross_return'], buy - sell)
        assert math.isclose(weights.loc[pd.Period('2020-04')].sum(), 0.0)

    def test_weights_use_only_earlier_months(self) -> None:
        """Checks that changing this month's deciles leaves its weights alone.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the weights change.
        """
        strategy = self._strategy()
        before = strategy.weights(10).loc[pd.Period('2020-03')].copy()
        strategy.deciles.loc[pd.Period('2020-03')] = [1.0, 1.0, 1.0, 1.0]
        after = strategy.weights(10).loc[pd.Period('2020-03')]
        assert before.equals(after)
