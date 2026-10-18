"""Tests for daily total returns."""

import math

import pandas as pd

from jegadeesh_titman_india.data.daily_returns_builder import (
    DailyReturnsBuilder,
)


class TestDailyReturnsBuilder:
    """Checks returns across corporate actions."""

    def _prices(self, closes: list[float], symbol: str = 'AAA') -> pd.DataFrame:
        """Makes a price table on consecutive days from 2020-01-01.

        Args:
            closes: The closing prices.
            symbol: The share's symbol.

        Returns:
            A table in the bhavcopy reader's format.

        Raises:
            None.
        """
        dates = pd.date_range('2020-01-01', periods=len(closes))
        return pd.DataFrame(
            {
                'date': dates,
                'symbol': symbol,
                'series': 'EQ',
                'close': closes,
                'traded_value': 1000.0,
            }
        )

    def _actions(
        self, ex_date: str, factor: float, dividend: float
    ) -> pd.DataFrame:
        """Makes a one-row action table.

        Args:
            ex_date: The ex-date.
            factor: The price factor.
            dividend: The dividend.

        Returns:
            The action table.

        Raises:
            None.
        """
        return pd.DataFrame(
            {
                'symbol': ['AAA'],
                'ex_date': [pd.Timestamp(ex_date)],
                'factor': [factor],
                'dividend': [dividend],
            }
        )

    def test_plain_return(self) -> None:
        """Checks a return with no corporate action.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        table, errors = DailyReturnsBuilder().build(
            self._prices([100.0, 110.0]),
            self._actions('2030-01-01', 2.0, 0.0),
        )
        assert math.isnan(table['ret'].iloc[0])
        assert math.isclose(table['ret'].iloc[1], 0.10)
        assert len(errors) == 0

    def test_bonus_one_for_one_is_not_a_loss(self) -> None:
        """Checks that a halved price after a 1:1 bonus gives a zero return.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        table, _ = DailyReturnsBuilder().build(
            self._prices([100.0, 50.0, 55.0]),
            self._actions('2020-01-02', 2.0, 0.0),
        )
        assert math.isclose(table['ret'].iloc[1], 0.0)
        assert math.isclose(table['ret'].iloc[2], 0.10)

    def test_dividend_adds_to_return(self) -> None:
        """Checks that a dividend counts as return on the ex-date.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        table, _ = DailyReturnsBuilder().build(
            self._prices([100.0, 98.0]),
            self._actions('2020-01-02', 1.0, 5.0),
        )
        assert math.isclose(table['ret'].iloc[1], 0.03)

    def test_action_on_a_non_trading_day_applies_next_trading_day(self) -> None:
        """Checks an ex-date that falls after the last close before a gap.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is wrong.
        """
        prices = self._prices([100.0, 100.0, 25.0])
        prices.loc[2, 'date'] = pd.Timestamp('2020-01-05')
        table, _ = DailyReturnsBuilder().build(
            prices,
            self._actions('2020-01-04', 4.0, 0.0),
        )
        assert math.isclose(table['ret'].iloc[2], 0.0)

    def test_missed_split_is_zeroed_and_logged(self) -> None:
        """Checks that an unexplained fall of 90 percent becomes zero.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the return is not zeroed or not logged.
        """
        table, errors = DailyReturnsBuilder().build(
            self._prices([100.0, 10.0]),
            self._actions('2030-01-01', 2.0, 0.0),
        )
        assert table['ret'].iloc[1] == 0.0
        assert len(errors) == 1
        assert math.isclose(errors['raw_return'].iloc[0], -0.9)

    def test_symbols_do_not_mix(self) -> None:
        """Checks that one share's close is never another's previous close.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the first return of the second share is set.
        """
        prices = pd.concat(
            [self._prices([100.0, 101.0]), self._prices([5.0, 5.5], 'BBB')],
            ignore_index=True,
        )
        table, _ = DailyReturnsBuilder().build(
            prices,
            self._actions('2030-01-01', 2.0, 0.0),
        )
        second = table[table['symbol'] == 'BBB']
        assert math.isnan(second['ret'].iloc[0])
        assert math.isclose(second['ret'].iloc[1], 0.10)
