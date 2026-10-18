"""Writes results/comparison.md against the earlier study's results."""

import pathlib
import sys

from jegadeesh_titman_india.reporting.comparison_writer import ComparisonWriter


class CompareApplication:
    """Runs the comparison writer.

    Attributes:
        mine: This study's results folder.
        theirs: The earlier study's results folder.
    """

    def __init__(self, mine: pathlib.Path, theirs: pathlib.Path) -> None:
        """Creates the application.

        Args:
            mine: This study's results folder.
            theirs: The earlier study's results folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.mine = mine
        self.theirs = theirs

    def run(self) -> None:
        """Writes the comparison.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        ComparisonWriter(self.mine, self.theirs).write()
        print('comparison written', flush=True)


if __name__ == '__main__':
    CompareApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
