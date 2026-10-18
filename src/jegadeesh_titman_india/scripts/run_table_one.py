"""Runs the strategy grid and writes Table I and the monthly series."""

import pathlib
import sys

import pandas as pd

from jegadeesh_titman_india.momentum.strategy_grid import StrategyGrid
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs


class RunTableOneApplication:
    """Runs all 64 strategies and saves the results.

    Attributes:
        data_folder: The study's data folder.
        results_folder: Where the tables are written.
    """

    def __init__(
        self,
        data_folder: pathlib.Path,
        results_folder: pathlib.Path,
    ) -> None:
        """Creates the application.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the tables are written.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.results_folder = results_folder

    def run(self) -> None:
        """Writes results/table_one.csv and data/derived/strategy_series.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        inputs = StudyInputs(self.data_folder)
        inputs.load()
        grid = StrategyGrid(inputs)
        table = grid.run()
        self.results_folder.mkdir(exist_ok=True)
        table.to_csv(self.results_folder / 'table_one.csv', index=False)
        series = pd.DataFrame(grid.series)
        series.index = series.index.astype(str)
        series.to_parquet(
            self.data_folder / 'derived' / 'strategy_series.parquet'
        )
        print('rows', len(table), flush=True)


if __name__ == '__main__':
    RunTableOneApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
