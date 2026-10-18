"""Reads one NSE share bhavcopy zip, in either file format."""

import datetime
import io
import pathlib
import zipfile

import pandas as pd


class BhavcopyReader:
    """Turns a bhavcopy zip into a table of one row per share.

    Attributes:
        series_priority: The series kept, best first.
    """

    COLUMNS: tuple[str, ...] = (
        'date',
        'symbol',
        'series',
        'close',
        'traded_value',
    )

    def __init__(self) -> None:
        """Sets the series that are kept.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.series_priority = {
            'EQ': 0,
            'BE': 1,
            'BZ': 2,
        }

    def read(self, path: pathlib.Path) -> pd.DataFrame:
        """Reads one zip file.

        Args:
            path: A file named like 2024-07-05.csv.zip.

        Returns:
            A table with columns date, symbol, series, close and
            traded_value, one row per share, preferring the EQ series.

        Raises:
            ValueError: When the file has neither known layout.
        """
        date = datetime.date.fromisoformat(path.name[:10])
        archive = zipfile.ZipFile(path)
        raw = archive.read(archive.namelist()[0])
        table = pd.read_csv(io.BytesIO(raw), index_col=False)
        if 'SYMBOL' in table.columns:
            table = self._from_old_layout(table)
        elif 'TckrSymb' in table.columns:
            table = self._from_udiff_layout(table)
        else:
            raise ValueError(f'Unknown bhavcopy layout in {path}')
        table['date'] = pd.Timestamp(date)
        return self._keep_one_row_per_share(table)

    def _from_old_layout(self, table: pd.DataFrame) -> pd.DataFrame:
        """Renames the columns of the layout used until July 2024.

        Args:
            table: The raw table.

        Returns:
            A table with symbol, series, close and traded_value.

        Raises:
            None.
        """
        return pd.DataFrame(
            {
                'symbol': table['SYMBOL'].str.strip(),
                'series': table['SERIES'].str.strip(),
                'close': table['CLOSE'],
                'traded_value': table['TOTTRDVAL'],
            }
        )

    def _from_udiff_layout(self, table: pd.DataFrame) -> pd.DataFrame:
        """Renames the columns of the layout used from July 2024.

        Args:
            table: The raw table.

        Returns:
            A table with symbol, series, close and traded_value, keeping
            only shares.

        Raises:
            None.
        """
        shares = table[table['FinInstrmTp'] == 'STK']
        return pd.DataFrame(
            {
                'symbol': shares['TckrSymb'].str.strip(),
                'series': shares['SctySrs'].str.strip(),
                'close': shares['ClsPric'],
                'traded_value': shares['TtlTrfVal'],
            }
        )

    def _keep_one_row_per_share(self, table: pd.DataFrame) -> pd.DataFrame:
        """Keeps EQ, BE and BZ rows with a positive close, one per symbol.

        Args:
            table: The table with date, symbol, series, close, traded_value.

        Returns:
            The filtered table in the standard column order.

        Raises:
            None.
        """
        table = table[table['series'].isin(self.series_priority)].copy()
        table = table[table['close'] > 0]
        table['priority'] = table['series'].map(self.series_priority)
        table = table.sort_values(['symbol', 'priority'])
        table = table.drop_duplicates('symbol', keep='first')
        return table[list(self.COLUMNS)].reset_index(drop=True)
