"""Writes the companion page's data files."""

import pathlib
import sys

from jegadeesh_titman_india.reporting.site_snapshot import SiteSnapshot


class BuildSnapshotApplication:
    """Runs the snapshot writer.

    Attributes:
        project: The study's folder.
    """

    def __init__(self, project: pathlib.Path) -> None:
        """Creates the application.

        Args:
            project: The study's folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.project = project

    def run(self) -> None:
        """Writes the snapshot.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        SiteSnapshot(
            self.project / 'results',
            self.project / 'data',
            self.project / 'paper',
            self.project / 'src/jegadeesh_titman_india/site/data',
        ).write()
        print('snapshot written', flush=True)


if __name__ == '__main__':
    BuildSnapshotApplication(pathlib.Path(sys.argv[1])).run()
