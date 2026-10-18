"""Tests for reading bhavcopy zip files."""

import pathlib
import zipfile

import pandas as pd

from jegadeesh_titman_india.data.bhavcopy_reader import BhavcopyReader


class TestBhavcopyReader:
    """Checks on both bhavcopy layouts."""

    def _zip(self, folder: pathlib.Path, name: str, text: str) -> pathlib.Path:
        """Writes a one-file zip.

        Args:
            folder: Where to write.
            name: The zip's file name.
            text: The CSV text inside.

        Returns:
            The zip's path.

        Raises:
            None.
        """
        path = folder / name
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('inner.csv', text)
        return path

    def test_old_layout_prefers_eq_and_drops_other_series(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Checks the old layout, with a trailing comma on every line.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the table is wrong.
        """
        text = (
            'SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,'
            'TOTTRDVAL,TIMESTAMP,\n'
            'AAA,BE,1,1,1,10,10,10,5,50,2-JAN-1995,\n'
            'AAA,EQ,1,1,1,11,11,10,5,55,2-JAN-1995,\n'
            'BBB,GB,1,1,1,12,12,10,5,60,2-JAN-1995,\n'
            'CCC,EQ,1,1,1,0,0,10,0,0,2-JAN-1995,\n'
        )
        path = self._zip(tmp_path, '1995-01-02.csv.zip', text)
        table = BhavcopyReader().read(path)
        assert list(table['symbol']) == ['AAA']
        assert table['close'].iloc[0] == 11
        assert table['series'].iloc[0] == 'EQ'
        assert table['date'].iloc[0] == pd.Timestamp('1995-01-02')
        assert not table['has_isin'].iloc[0]

    def test_udiff_layout_keeps_shares_only(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Checks the layout used from July 2024.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the table is wrong.
        """
        text = (
            'TradDt,FinInstrmTp,TckrSymb,SctySrs,ClsPric,TtlTrfVal,ISIN\n'
            '2026-10-06,STK,AAA,EQ,100,5000,INE000A01010\n'
            '2026-10-06,GOVT,SGB,GB,6000,9000,IN0020200104\n'
            '2026-10-06,STK,BBB,BZ,20,400,INF204KB17I5\n'
        )
        path = self._zip(tmp_path, '2026-10-06.csv.zip', text)
        table = BhavcopyReader().read(path)
        assert sorted(table['symbol']) == ['AAA', 'BBB']
        by_symbol = table.set_index('symbol')
        assert by_symbol.loc['BBB', 'traded_value'] == 400
        assert by_symbol.loc['BBB', 'is_fund']
        assert not by_symbol.loc['AAA', 'is_fund']
