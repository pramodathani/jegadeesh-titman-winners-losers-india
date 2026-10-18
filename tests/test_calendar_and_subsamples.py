"""Tests for subsamples and calendar tables."""

import math

import numpy as np
import pandas as pd

from jegadeesh_titman_india.momentum.calendar_tables import CalendarTables
from jegadeesh_titman_india.momentum.subsamples import Subsamples


class TestSubsamples:
    """Checks on terciles."""

    def test_terciles_split_eligible_shares_into_thirds(self) -> None:
        """Checks six shares split two each, ignoring an ineligible share.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the thirds are wrong.
        """
        months = pd.period_range('2020-01', periods=1, freq='M')
        names = list('ABCDEFG')
        values = pd.DataFrame(
            [[7, 1, 5, 3, 2, 6, 4]], index=months, columns=names
        )
        eligible = pd.DataFrame(True, index=months, columns=names)
        eligible.loc[months[0], 'A'] = False
        thirds = Subsamples().terciles(values.astype(float), eligible)
        assert list(thirds[1].loc[months[0]][names]) == [
            False,
            True,
            False,
            False,
            True,
            False,
            False,
        ]
        assert thirds[3].loc[months[0]].sum() == 2
        assert not thirds[3].loc[months[0], 'A']

    def test_beta_terciles_use_the_previous_year(self) -> None:
        """Checks that January 2021 uses the 2020 betas.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the wrong year is used.
        """
        months = pd.period_range('2021-01', periods=1, freq='M')
        names = list('ABC')
        betas = pd.DataFrame(
            [[0.5, 1.0, 1.5], [1.5, 1.0, 0.5]],
            index=[2020, 2021],
            columns=names,
        )
        eligible = pd.DataFrame(True, index=months, columns=names)
        thirds = Subsamples().beta_terciles(betas, eligible)
        assert thirds[1].loc[months[0], 'A']
        assert thirds[3].loc[months[0], 'C']


class TestCalendarTables:
    """Checks on seasonal means."""

    def test_calendar_month_means_and_positive_share(self) -> None:
        """Checks March and January means over two years.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a mean is wrong.
        """
        months = pd.period_range('2007-01', periods=24, freq='M')
        values = np.where(months.month == 1, -0.04, 0.01)
        values = np.where(months.month == 3, 0.03, values)
        zero_cost = pd.DataFrame({'All': values}, index=months)
        table = CalendarTables().by_calendar_month(zero_cost)
        january = table[table['months'] == 'Jan'].iloc[0]
        march = table[table['months'] == 'Mar'].iloc[0]
        assert math.isclose(january['mean'], -0.04)
        assert january['positive_share'] == 0.0
        assert math.isclose(march['mean'], 0.03)
        assert march['observations'] == 2

    def test_subperiods_split_the_sample(self) -> None:
        """Checks that subperiod means reflect their own months.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a mean is wrong.
        """
        months = pd.period_range('2007-01', '2026-09', freq='M')
        values = np.where(months.year < 2012, 0.02, 0.0)
        zero_cost = pd.DataFrame({'All': values}, index=months)
        table = CalendarTables().by_subperiod(zero_cost)
        first = table[
            (table['subperiod'] == '2007-2011') & (table['months'] == 'All')
        ]
        second = table[
            (table['subperiod'] == '2012-2016') & (table['months'] == 'All')
        ]
        assert math.isclose(first['mean'].iloc[0], 0.02)
        assert math.isclose(second['mean'].iloc[0], 0.0)
