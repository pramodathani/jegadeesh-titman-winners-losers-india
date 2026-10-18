"""Writes results/summary.md."""

import pathlib
import sys

from jegadeesh_titman_india.reporting.summary_writer import SummaryWriter


class WriteSummaryApplication:
    """Runs the summary writer.

    Attributes:
        results: The results folder.
        paper: The paper folder.
    """

    def __init__(self, results: pathlib.Path, paper: pathlib.Path) -> None:
        """Creates the application.

        Args:
            results: The results folder.
            paper: The paper folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.results = results
        self.paper = paper

    def run(self) -> None:
        """Writes the summary.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        SummaryWriter(self.results, self.paper).write()
        print('summary written', flush=True)


if __name__ == '__main__':
    WriteSummaryApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
