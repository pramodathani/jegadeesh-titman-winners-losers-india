"""Builds the daily total returns table from the raw bhavcopies."""

import pathlib
import sys

import pandas as pd

from jegadeesh_titman_india.data.bhavcopy_reader import BhavcopyReader
from jegadeesh_titman_india.data.corporate_actions import CorporateActionTable
from jegadeesh_titman_india.data.daily_returns_builder import (
    DailyReturnsBuilder,
)


class BuildDailyReturnsApplication:
    """Reads every bhavcopy and writes daily returns.

    Attributes:
        data_folder: The study's data folder.
    """

    def __init__(self, data_folder: pathlib.Path) -> None:
        """Creates the application.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder

    def run(self) -> None:
        """Writes derived/daily_returns.parquet and derived/data_errors.csv.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        reader = BhavcopyReader()
        files = sorted(
            (self.data_folder / 'external/earlier_bhavcopy_raw').glob(
                '[12]*/*.csv.zip'
            )
        )
        files += sorted(
            (self.data_folder / 'nse/bhavcopy_raw').glob('[12]*/*.csv.zip')
        )
        by_date = {}
        for path in files:
            by_date[path.name[:10]] = path
        frames = []
        for position, name in enumerate(sorted(by_date)):
            frames.append(reader.read(by_date[name]))
            if position % 500 == 0:
                print('read', name, flush=True)
        prices = pd.concat(frames, ignore_index=True)
        print('price rows', len(prices), flush=True)
        action_files = sorted(
            (self.data_folder / 'external/earlier_corporate_actions').glob(
                '*.json'
            )
        )
        action_files = [
            path for path in action_files if path.name != '2026.json'
        ]
        action_files.append(
            self.data_folder / 'nse/corporate_actions/2026.json'
        )
        actions = CorporateActionTable().load(action_files)
        print('actions', len(actions), flush=True)
        table, errors = DailyReturnsBuilder().build(prices, actions)
        folder = self.data_folder / 'derived'
        folder.mkdir(exist_ok=True)
        table.to_parquet(folder / 'daily_returns.parquet', index=False)
        errors.to_csv(folder / 'data_errors.csv', index=False)
        print('rows', len(table), 'errors', len(errors), flush=True)


if __name__ == '__main__':
    BuildDailyReturnsApplication(pathlib.Path(sys.argv[1])).run()
