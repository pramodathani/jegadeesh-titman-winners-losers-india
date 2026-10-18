"""Tests for the announcement-return table."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.earnings_table import EarningsTable


class TestEarningsTable:
    """Checks on event days and three-day returns."""

    def _sessions(self) -> pd.DatetimeIndex:
        """Makes ten consecutive weekday sessions from 2020-03-02.

        Args:
            None.

        Returns:
            The sessions.

        Raises:
            None.
        """
        return pd.bdate_range('2020-03-02', periods=10)

    def test_after_hours_announcement_moves_to_the_next_session(self) -> None:
        """Checks a 16:00 filing and a 10:00 filing on the same date.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the positions are wrong.
        """
        announced = pd.Series(
            pd.to_datetime(
                [
                    '2020-03-04 10:00',
                    '2020-03-04 16:00',
                    '2020-03-07 11:00',
                    '2021-01-01 11:00',
                ]
            )
        )
        positions = EarningsTable().event_positions(announced, self._sessions())
        assert list(positions) == [2, 3, 5, -1]

    def test_three_day_return_compounds_days_minus_two_to_zero(self) -> None:
        """Checks a window of three returns and one with too few trades.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a return is wrong.
        """
        returns = pd.DataFrame(
            {
                'A': [0.01 * number for number in range(10)],
                'B': [np.nan] * 5 + [0.1] * 5,
            },
            index=self._sessions(),
        )
        announcements = pd.DataFrame({'symbol': ['A', 'B', 'Z']})
        result = EarningsTable().window_returns(
            returns,
            announcements,
            np.array([4, 4, 4]),
        )
        assert math.isclose(result[0], 1.02 * 1.03 * 1.04 - 1.0)
        assert math.isnan(result[1])
        assert math.isnan(result[2])

    def test_table_gives_winner_minus_loser_by_month_since_ranking(
        self,
    ) -> None:
        """Checks a case where the winner always beats the loser.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the difference is wrong.
        """
        sessions = pd.bdate_range('2020-01-01', '2020-12-31')
        returns = pd.DataFrame(
            {'W': 0.01, 'L': -0.01},
            index=sessions,
        )
        months = pd.period_range('2019-01', '2020-12', freq='M')
        deciles = pd.DataFrame(
            {'W': 10.0, 'L': 1.0},
            index=months,
        )
        announcements = pd.DataFrame(
            {
                'symbol': ['W', 'L', 'W', 'L'],
                'announced': pd.to_datetime(
                    [
                        '2020-06-10 11:00',
                        '2020-06-10 11:00',
                        '2020-07-10 11:00',
                        '2020-07-10 11:00',
                    ]
                ),
            }
        )
        table = EarningsTable(horizon=3).table(announcements, returns, deciles)
        expected = (1.01**3 - 1.0) - (0.99**3 - 1.0)
        assert math.isclose(table.loc[0, 'winners_minus_losers'], expected)
        assert table.loc[0, 'winner_announcements'] == 2
        assert table.loc[0, 'formation_months'] == 2
