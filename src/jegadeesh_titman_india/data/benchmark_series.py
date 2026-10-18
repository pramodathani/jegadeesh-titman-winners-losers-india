"""Loads the NIFTY 500 total return index and the IIMA factors."""

import json
import pathlib

import pandas as pd


class BenchmarkSeries:
    """The market index and risk-free rate used for alphas and betas.

    Attributes:
        index_levels: The NIFTY 500 total return index by date.
    """

    def __init__(self, tri_path: pathlib.Path) -> None:
        """Reads the index file.

        Args:
            tri_path: The JSON file written by the downloader.

        Returns:
            None.

        Raises:
            None.
        """
        rows = json.loads(tri_path.read_text())
        table = pd.DataFrame(rows)
        table['date'] = pd.to_datetime(table['Date'], format='%d %b %Y')
        levels = pd.to_numeric(table['TotalReturnsIndex'], errors='coerce')
        self.index_levels = pd.Series(
            levels.to_numpy(),
            index=table['date'],
        ).sort_index()

    def daily_returns(self, sessions: pd.DatetimeIndex) -> pd.Series:
        """Gives the index's return on each trading session.

        Args:
            sessions: The trading dates wanted.

        Returns:
            Returns by session; the return on a session is the index's change
            since the previous session in the list, NaN when the index has no
            level on either date.

        Raises:
            None.
        """
        levels = self.index_levels.reindex(sessions)
        return levels.pct_change(fill_method=None)

    def monthly_returns(self) -> pd.Series:
        """Gives the index's return in each calendar month.

        Args:
            None.

        Returns:
            Returns by month, from the last level of each month.

        Raises:
            None.
        """
        months = self.index_levels.index.to_period('M')
        month_end = self.index_levels.groupby(months).last()
        return month_end.pct_change()


class IimaFactors:
    """The IIMA monthly factors and risk-free return, as fractions.

    Attributes:
        table: Columns SMB, HML, WML, MF and RF, indexed by month.
    """

    def __init__(self, path: pathlib.Path) -> None:
        """Reads the CSV, which holds percentages.

        Args:
            path: The IIMA monthly CSV.

        Returns:
            None.

        Raises:
            None.
        """
        table = pd.read_csv(path)
        table.index = pd.PeriodIndex(table['Date'], freq='M')
        self.table = table.drop(columns=['Date']) / 100.0
