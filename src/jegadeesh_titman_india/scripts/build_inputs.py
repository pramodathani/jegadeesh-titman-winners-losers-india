"""Builds the monthly inputs from the daily returns table."""

import pathlib
import sys

import pandas as pd

from jegadeesh_titman_india.momentum.study_inputs import StudyInputs


class BuildInputsApplication:
    """Writes the cached monthly inputs.

    Attributes:
        data_folder: The study's data folder.
        last_month: The last complete month.
    """

    def __init__(self, data_folder: pathlib.Path, last_month: str) -> None:
        """Creates the application.

        Args:
            data_folder: The study's data folder.
            last_month: The last complete month as YYYY-MM.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.last_month = pd.Period(last_month, freq='M')

    def run(self) -> None:
        """Builds and saves the inputs.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        StudyInputs(self.data_folder).build(self.last_month)
        print('inputs built', flush=True)


if __name__ == '__main__':
    BuildInputsApplication(pathlib.Path(sys.argv[1]), sys.argv[2]).run()
