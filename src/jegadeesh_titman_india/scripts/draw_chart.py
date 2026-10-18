"""Draws results/figures/wealth.png."""

import pathlib
import sys

from jegadeesh_titman_india.reporting.wealth_chart import WealthChart


class DrawChartApplication:
    """Runs the wealth chart.

    Attributes:
        data_folder: The study's data folder.
        target: The PNG file.
    """

    def __init__(self, data_folder: pathlib.Path, target: pathlib.Path) -> None:
        """Creates the application.

        Args:
            data_folder: The study's data folder.
            target: The PNG file.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.target = target

    def run(self) -> None:
        """Draws the chart.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        WealthChart(self.data_folder).draw(
            self.target,
            self.target.parent.parent / 'wealth_by_year.csv',
        )
        print('chart written', flush=True)


if __name__ == '__main__':
    DrawChartApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
