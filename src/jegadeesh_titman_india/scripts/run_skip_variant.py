"""Runs the skip variant that ends the ranking window a week early."""

import pathlib
import sys

from jegadeesh_titman_india.momentum.earlier_ranking_skip import (
    EarlierRankingSkip,
)
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs


class RunSkipVariantApplication:
    """Writes results/table_one_earlier_ranking_skip.csv.

    Attributes:
        data_folder: The study's data folder.
        results_folder: Where the table is written.
    """

    def __init__(
        self,
        data_folder: pathlib.Path,
        results_folder: pathlib.Path,
    ) -> None:
        """Creates the application.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the table is written.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.results_folder = results_folder

    def run(self) -> None:
        """Runs the variant.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        inputs = StudyInputs(self.data_folder)
        inputs.load()
        table = EarlierRankingSkip(inputs).table()
        table.to_csv(
            self.results_folder / 'table_one_earlier_ranking_skip.csv',
            index=False,
        )
        print('rows', len(table), flush=True)


if __name__ == '__main__':
    RunSkipVariantApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
