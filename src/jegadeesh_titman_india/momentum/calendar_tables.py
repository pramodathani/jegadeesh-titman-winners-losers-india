"""Tables IV, V and VI: calendar months and subperiods of winners-minus-losers."""

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.study_settings import StudySettings


class CalendarTables:
    """Seasonal and subperiod views of monthly zero-cost returns.

    Attributes:
        statistics: The return statistics helper.
    """

    SUBPERIODS: tuple[tuple[str, str], ...] = (
        ('2007-01', '2011-12'),
        ('2012-01', '2016-12'),
        ('2017-01', '2021-12'),
        ('2022-01', '2026-09'),
    )

    def __init__(self) -> None:
        """Creates the helper.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.statistics = ReturnStatistics()

    def _main(self, zero_cost: pd.DataFrame) -> pd.DataFrame:
        """Restricts returns to the main sample.

        Args:
            zero_cost: Monthly returns, months by subsamples.

        Returns:
            The main-sample rows.

        Raises:
            None.
        """
        return zero_cost.loc[StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST]

    def by_calendar_month(self, zero_cost: pd.DataFrame) -> pd.DataFrame:
        """Gives mean return, t-statistic and share of positive months.

        Rows are the twelve calendar months, then Feb-Dec (the paper's
        non-January months), Apr-Feb (months other than March) and All.

        Args:
            zero_cost: Monthly P10-P1 returns, months by subsamples.

        Returns:
            Rows by calendar month and subsample with columns mean, t and
            positive_share.

        Raises:
            None.
        """
        main = self._main(zero_cost)
        names = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
        ]
        groups = {
            name: main.index.month == number + 1
            for number, name in enumerate(names)
        }
        groups['Feb-Dec'] = main.index.month != 1
        groups['All except Mar'] = main.index.month != 3
        groups['All'] = main.index.month > 0
        rows = []
        for group, selected in groups.items():
            for subsample in main.columns:
                series = main.loc[selected, subsample].dropna()
                mean, t_statistic = self.statistics.mean_and_t(series)
                rows.append(
                    {
                        'months': group,
                        'subsample': subsample,
                        'mean': mean,
                        't': t_statistic,
                        'positive_share': float((series > 0).mean()),
                        'observations': len(series),
                    }
                )
        return pd.DataFrame(rows)

    def by_subperiod(self, zero_cost: pd.DataFrame) -> pd.DataFrame:
        """Gives mean returns in four subperiods, all months and split by month.

        Args:
            zero_cost: Monthly P10-P1 returns, months by subsamples.

        Returns:
            Rows by subperiod, month group and subsample.

        Raises:
            None.
        """
        rows = []
        for first, last in self.SUBPERIODS:
            window = zero_cost.loc[first:last]
            groups = {
                'All': window.index.month > 0,
                'Jan': window.index.month == 1,
                'Feb-Dec': window.index.month != 1,
                'Mar': window.index.month == 3,
                'All except Mar': window.index.month != 3,
            }
            for group, selected in groups.items():
                for subsample in window.columns:
                    series = window.loc[selected, subsample].dropna()
                    mean, t_statistic = self.statistics.mean_and_t(series)
                    rows.append(
                        {
                            'subperiod': f'{first[:4]}-{last[:4]}',
                            'months': group,
                            'subsample': subsample,
                            'mean': mean,
                            't': t_statistic,
                            'observations': len(series),
                        }
                    )
        return pd.DataFrame(rows)
