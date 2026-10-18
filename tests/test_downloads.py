"""Tests for the download addresses and file layout."""

import datetime
import pathlib

from jegadeesh_titman_india.data.downloads import BhavcopyTopUp
from jegadeesh_titman_india.data.nse_session import NseSession


class TestBhavcopyTopUp:
    """Checks on which address is used for which date."""

    def _downloader(self, folder: pathlib.Path) -> BhavcopyTopUp:
        """Makes a downloader that never touches the network.

        Args:
            folder: The folder for files.

        Returns:
            The downloader.

        Raises:
            None.
        """
        return BhavcopyTopUp(folder, NseSession())

    def test_old_layout_until_july_2024(self, tmp_path: pathlib.Path) -> None:
        """Checks the address of a 1995 file and of the last old-layout day.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When an address is wrong.
        """
        downloader = self._downloader(tmp_path)
        assert downloader.url(datetime.date(1995, 1, 2)).endswith(
            '/1995/JAN/cm02JAN1995bhav.csv.zip'
        )
        assert downloader.url(datetime.date(2024, 7, 5)).endswith(
            '/2024/JUL/cm05JUL2024bhav.csv.zip'
        )

    def test_new_layout_from_july_2024(self, tmp_path: pathlib.Path) -> None:
        """Checks the address of the first UDiFF day.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the address is wrong.
        """
        downloader = self._downloader(tmp_path)
        assert downloader.url(datetime.date(2024, 7, 8)).endswith(
            'BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv.zip'
        )
