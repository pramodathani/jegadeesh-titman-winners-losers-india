"""Small made-up daily tables shared by the tests."""

import pandas as pd


class PanelFixtures:
    """Builds daily tables with known answers."""

    def daily(self) -> pd.DataFrame:
        """Makes twelve sessions for three shares.

        Share A and B trade every session, share C only in the first six.
        A's return on session q is 0.01 times q plus one.

        Args:
            None.

        Returns:
            A table with columns date, symbol, traded_value and ret.

        Raises:
            None.
        """
        dates = pd.to_datetime(
            [
                '2020-01-01',
                '2020-01-02',
                '2020-01-03',
                '2020-02-03',
                '2020-02-04',
                '2020-02-05',
                '2020-03-02',
                '2020-03-03',
                '2020-03-04',
                '2020-04-01',
                '2020-04-02',
                '2020-04-03',
            ]
        )
        rows = []
        for position, date in enumerate(dates):
            rows.append(
                {
                    'date': date,
                    'symbol': 'A',
                    'traded_value': 100.0,
                    'ret': 0.01 * (position + 1),
                }
            )
            rows.append(
                {
                    'date': date,
                    'symbol': 'B',
                    'traded_value': 50.0,
                    'ret': 0.0,
                }
            )
            if position < 6:
                rows.append(
                    {
                        'date': date,
                        'symbol': 'C',
                        'traded_value': 10.0,
                        'ret': -0.01,
                    }
                )
        return pd.DataFrame(rows)
