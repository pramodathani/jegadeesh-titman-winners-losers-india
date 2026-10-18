"""Runs every table after Table I and writes the results folder."""

import pathlib
import sys

import pandas as pd

from jegadeesh_titman_india.data.results_announcements import (
    ResultsAnnouncements,
)
from jegadeesh_titman_india.momentum.calendar_tables import CalendarTables
from jegadeesh_titman_india.momentum.decile_tables import DecileTables
from jegadeesh_titman_india.momentum.earnings_table import EarningsTable
from jegadeesh_titman_india.momentum.event_time import (
    EventTimeReturns,
    EventTimeSummary,
)
from jegadeesh_titman_india.momentum.headline_strategies import (
    HeadlineStrategies,
)
from jegadeesh_titman_india.momentum.section_three import SectionThree
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class RunAllTablesApplication:
    """Writes Tables II to IX, Section III and the headline strategies.

    Attributes:
        data_folder: The study's data folder.
        results_folder: Where the tables are written.
        inputs: The loaded study inputs.
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
        self.inputs = StudyInputs(data_folder)

    def run(self) -> None:
        """Runs everything.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.inputs.load()
        self.results_folder.mkdir(exist_ok=True)
        self.deciles_and_calendar()
        self.event_time_and_section_three()
        self.earnings()
        self.headline()
        self.cross_check()

    def save(self, table: pd.DataFrame, name: str) -> None:
        """Writes a table to the results folder.

        Args:
            table: The table.
            name: The file name without the extension.

        Returns:
            None.

        Raises:
            None.
        """
        table.to_csv(self.results_folder / f'{name}.csv', index=False)
        print('wrote', name, len(table), flush=True)

    def deciles_and_calendar(self) -> None:
        """Writes Tables II, III, IV, V and VI.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        tables = DecileTables(self.inputs)
        calendar = CalendarTables()
        two, three, four, six = [], [], [], []
        series = {}
        for universe in ('A', 'B'):
            two.append(tables.table_two(universe))
            scored, zero_cost = tables.table_three(universe)
            three.append(scored)
            for name in zero_cost.columns:
                series[f'{universe}_{name}'] = zero_cost[name]
            by_month = calendar.by_calendar_month(zero_cost)
            by_month.insert(0, 'universe', universe)
            four.append(by_month)
            by_period = calendar.by_subperiod(zero_cost)
            by_period.insert(0, 'universe', universe)
            six.append(by_period)
        self.save(pd.concat(two), 'table_two')
        self.save(pd.concat(three), 'table_three')
        self.save(pd.concat(four), 'table_four_five')
        self.save(pd.concat(six), 'table_six')
        frame = pd.DataFrame(series)
        frame.index = frame.index.astype(str)
        frame.to_parquet(self.data_folder / 'derived' / 'zero_cost_6_6.parquet')

    def event_time_and_section_three(self) -> None:
        """Writes Tables VII and VIII and the Section III results.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        tables = DecileTables(self.inputs)
        summary = EventTimeSummary()
        seven, eight, three = [], [], []
        for universe in ('A', 'B'):
            strategy = tables.strategy(tables.mask(universe), 100)
            event = EventTimeReturns(
                strategy.deciles,
                self.inputs.standard_returns,
                36,
            )
            zero_cost = event.zero_cost()
            main = summary.summarize(
                zero_cost,
                StudySettings.MAIN_FIRST - 1,
                pd.Period('2023-09', freq='M'),
            )
            main.insert(0, 'universe', universe)
            seven.append(main)
            early = summary.summarize(
                zero_cost,
                StudySettings.EARLY_FIRST - 1,
                StudySettings.EARLY_LAST - 1,
            )
            early.insert(0, 'universe', universe)
            eight.append(early)
            result = SectionThree().table(
                self.inputs.standard_returns,
                tables.mask(universe),
                strategy.deciles,
                self.inputs.market_monthly,
            )
            result.insert(0, 'universe', universe)
            three.append(result)
        self.save(pd.concat(seven), 'table_seven')
        self.save(pd.concat(eight), 'table_eight_early_sample')
        self.save(pd.concat(three), 'section_three')

    def earnings(self) -> None:
        """Writes Table IX.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        daily = pd.read_parquet(
            self.data_folder / 'derived' / 'daily_returns.parquet',
            columns=['date', 'symbol', 'ret'],
        )
        panel = daily.pivot(index='date', columns='symbol', values='ret')
        del daily
        announcements = ResultsAnnouncements().load(
            self.data_folder / 'nse' / 'results'
        )
        announcements = announcements[
            (announcements['announced'] >= '2007-08-01')
            & (announcements['announced'] < '2025-04-01')
        ]
        tables = DecileTables(self.inputs)
        frames = []
        for universe in ('A', 'B'):
            strategy = tables.strategy(tables.mask(universe), 100)
            result = EarningsTable().table(
                announcements,
                panel,
                strategy.deciles,
            )
            result.insert(0, 'universe', universe)
            frames.append(result)
        self.save(pd.concat(frames), 'table_nine')

    def headline(self) -> None:
        """Writes the headline strategies with cost sensitivity.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        table = HeadlineStrategies(self.inputs).table()
        self.save(table, 'headline_strategies')

    def cross_check(self) -> None:
        """Writes the correlation of our series with IIMA's WML factor.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        series = pd.read_parquet(
            self.data_folder / 'derived' / 'strategy_series.parquet'
        )
        series.index = pd.PeriodIndex(series.index, freq='M')
        factor = self.inputs.wml_iima.dropna()
        rows = []
        for name in series.columns:
            if not name.endswith('_bs_gross'):
                continue
            ours = series[name].loc['2007-01':'2025-12']
            theirs = factor.loc['2007-01':'2025-12']
            rows.append(
                {
                    'strategy': name.removesuffix('_bs_gross'),
                    'correlation_with_iima_wml': ours.corr(theirs),
                    'our_mean': ours.mean(),
                    'iima_mean': theirs.mean(),
                    'months': int(
                        pd.concat([ours, theirs], axis=1).dropna().shape[0]
                    ),
                }
            )
        self.save(pd.DataFrame(rows), 'cross_check_iima')


if __name__ == '__main__':
    RunAllTablesApplication(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
    ).run()
