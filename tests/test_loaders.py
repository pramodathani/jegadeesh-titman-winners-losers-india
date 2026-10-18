"""Tests for the benchmark, IIMA and results loaders."""

import json
import math
import pathlib

import pandas as pd

from jegadeesh_titman_india.data.benchmark_series import (
    BenchmarkSeries,
    IimaFactors,
)
from jegadeesh_titman_india.data.results_announcements import (
    ResultsAnnouncements,
)


class TestLoaders:
    """Checks on reading the downloaded files."""

    def test_benchmark_monthly_and_daily_returns(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Checks returns from a three-row index file.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When a return is wrong.
        """
        rows = [
            {'Date': '31 Jan 2020', 'TotalReturnsIndex': '100.00'},
            {'Date': '03 Feb 2020', 'TotalReturnsIndex': '102.00'},
            {'Date': '28 Feb 2020', 'TotalReturnsIndex': '110.00'},
        ]
        path = tmp_path / 'tri.json'
        path.write_text(json.dumps(rows))
        benchmark = BenchmarkSeries(path)
        monthly = benchmark.monthly_returns()
        assert math.isclose(monthly.loc[pd.Period('2020-02')], 0.10)
        sessions = pd.to_datetime(['2020-01-31', '2020-02-03', '2020-02-04'])
        daily = benchmark.daily_returns(sessions)
        assert math.isclose(daily.iloc[1], 0.02)
        assert math.isnan(daily.iloc[2])

    def test_iima_factors_are_fractions(self, tmp_path: pathlib.Path) -> None:
        """Checks that percentages become fractions with a monthly index.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When a value is wrong.
        """
        path = tmp_path / 'iima.csv'
        path.write_text('Date,SMB,HML,WML,MF,RF\n1995-01,1,2,3,4,0.9\n')
        factors = IimaFactors(path)
        assert math.isclose(
            factors.table.loc[pd.Period('1995-01'), 'RF'], 0.009
        )
        assert math.isclose(
            factors.table.loc[pd.Period('1995-01'), 'WML'], 0.03
        )

    def test_results_announcements_keep_the_earliest_time(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Checks that standalone and consolidated filings become one row.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the table is wrong.
        """
        rows = [
            {
                'symbol': 'AAA',
                'toDate': '30-Jun-2020',
                'broadCastDate': '10-Aug-2020 16:00:00',
                'filingDate': '10-Aug-2020 16:05',
            },
            {
                'symbol': 'AAA',
                'toDate': '30-Jun-2020',
                'broadCastDate': '09-Aug-2020 11:00:00',
                'filingDate': '09-Aug-2020 11:30',
            },
            {
                'symbol': 'BBB',
                'toDate': '30-Jun-2007',
                'broadCastDate': None,
                'filingDate': '01-Aug-2007 12:00',
            },
        ]
        (tmp_path / '2020.json').write_text(json.dumps(rows))
        table = ResultsAnnouncements().load(tmp_path)
        assert len(table) == 2
        first = table[table['symbol'] == 'AAA'].iloc[0]
        assert first['announced'] == pd.Timestamp('2020-08-09 11:00:00')
        second = table[table['symbol'] == 'BBB'].iloc[0]
        assert second['announced'] == pd.Timestamp('2007-08-01 12:00:00')
