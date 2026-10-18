"""Tests for the companion page's snapshot and local server."""

import json
import pathlib

import pandas as pd
import pytest

from jegadeesh_titman_india.reporting.site_snapshot import SiteSnapshot
from jegadeesh_titman_india.site_server import SiteServerApplication


class TestSiteSnapshot:
    """Checks on the snapshot's JSON."""

    def _snapshot(self, tmp_path: pathlib.Path) -> SiteSnapshot:
        """Makes a snapshot writer with empty folders.

        Args:
            tmp_path: A temporary folder.

        Returns:
            The writer.

        Raises:
            None.
        """
        return SiteSnapshot(tmp_path, tmp_path, tmp_path, tmp_path / 'out')

    def test_rounded_gives_null_for_gaps(self, tmp_path: pathlib.Path) -> None:
        """Checks rounding to six decimals and null for NaN.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the list is wrong.
        """
        series = pd.Series([0.1234567891, float('nan'), -0.5])
        result = self._snapshot(tmp_path).rounded(series)
        assert result == [0.123457, None, -0.5]

    def test_dump_refuses_nan(self, tmp_path: pathlib.Path) -> None:
        """Checks that invalid JSON numbers are never written.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When NaN is accepted.
        """
        snapshot = self._snapshot(tmp_path)
        snapshot.target.mkdir()
        snapshot.dump('ok', {'value': [1, 2]})
        assert json.loads((snapshot.target / 'ok.json').read_text()) == {
            'value': [1, 2],
        }
        with pytest.raises(ValueError, match='Out of range'):
            snapshot.dump('bad', {'value': float('nan')})


class TestSiteServer:
    """Checks on the local server's helpers."""

    def test_page_is_shipped_in_the_package(self) -> None:
        """Checks that index.html and the data files exist.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When a file is missing.
        """
        folder = SiteServerApplication.SITE_DIRECTORY
        assert (folder / 'index.html').exists()
        assert (folder / 'app.js').exists()
        assert (folder / 'data' / 'returns.json').exists()

    def test_free_port_returns_a_port_in_range(self) -> None:
        """Checks that a free port near the preferred one is found.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the port is out of range.
        """
        port = SiteServerApplication().free_port(18000)
        assert 18000 <= port < 18020
