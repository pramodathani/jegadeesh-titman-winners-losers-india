"""Reads NSE quarterly results filings into announcement times."""

import json
import pathlib

import pandas as pd


class ResultsAnnouncements:
    """One announcement time per share and quarter."""

    def load(self, folder: pathlib.Path) -> pd.DataFrame:
        """Reads every yearly JSON file in a folder.

        The announcement time is the earliest broadcast time among a
        quarter's filings, falling back to the filing time when no broadcast
        time is given. Standalone and consolidated filings count as one.

        Args:
            folder: The folder with the yearly JSON files.

        Returns:
            A table with columns symbol, quarter_end and announced, one row
            per share and quarter.

        Raises:
            None.
        """
        frames = []
        for path in sorted(folder.glob('*.json')):
            rows = json.loads(path.read_text())
            if rows:
                frames.append(pd.DataFrame(rows))
        table = pd.concat(frames, ignore_index=True)
        broadcast = pd.to_datetime(
            table['broadCastDate'],
            format='%d-%b-%Y %H:%M:%S',
            errors='coerce',
        )
        filing = pd.to_datetime(
            table['filingDate'],
            format='%d-%b-%Y %H:%M',
            errors='coerce',
        )
        announced = broadcast.fillna(filing)
        result = pd.DataFrame(
            {
                'symbol': table['symbol'].str.strip(),
                'quarter_end': pd.to_datetime(
                    table['toDate'],
                    format='%d-%b-%Y',
                    errors='coerce',
                ),
                'announced': announced,
            }
        )
        result = result.dropna()
        grouped = result.groupby(['symbol', 'quarter_end'])['announced']
        earliest = grouped.min().reset_index()
        return earliest
