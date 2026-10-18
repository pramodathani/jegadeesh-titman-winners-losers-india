"""Writes the companion page's data files from the derived results."""

import datetime
import json
import pathlib

import pandas as pd

from jegadeesh_titman_india.data.benchmark_series import BenchmarkSeries
from jegadeesh_titman_india.momentum.study_settings import StudySettings
from jegadeesh_titman_india.reporting.paper_numbers import PaperNumbers


class SiteSnapshot:
    """Compact JSON of the study's results for the web page.

    Only derived results are written: monthly returns of the strategies,
    the benchmark's monthly returns and the results tables. No raw exchange
    prices are included.

    Attributes:
        results: The results folder.
        data_folder: The study's data folder.
        paper: The paper folder.
        target: The site's data folder.
    """

    SERIES: tuple[tuple[str, str], ...] = (
        ('lo', 'buy_net'),
        ('ls', 'bs_net'),
        ('lsg', 'bs_gross'),
        ('turnover', 'buy_turnover'),
    )
    TABLES: tuple[str, ...] = (
        'table_one',
        'table_one_earlier_ranking_skip',
        'table_two',
        'table_three',
        'table_four_five',
        'table_six',
        'table_seven',
        'table_eight_early_sample',
        'table_nine',
        'section_three',
        'headline_strategies',
        'robustness',
        'delisting_stress',
        'cross_check_iima',
        'wealth_by_year',
    )

    def __init__(
        self,
        results: pathlib.Path,
        data_folder: pathlib.Path,
        paper: pathlib.Path,
        target: pathlib.Path,
    ) -> None:
        """Creates the snapshot writer.

        Args:
            results: The results folder.
            data_folder: The study's data folder.
            paper: The paper folder.
            target: The site's data folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.results = results
        self.data_folder = data_folder
        self.paper = paper
        self.target = target

    def write(self) -> None:
        """Writes returns.json, tables.json and meta.json.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.target.mkdir(parents=True, exist_ok=True)
        returns = self.returns()
        self.dump('returns', returns)
        self.dump('tables', self.tables())
        self.dump('meta', self.meta(returns))

    def dump(self, name: str, content: dict) -> None:
        """Writes one JSON file without extra spaces.

        Args:
            name: The file name without the extension.
            content: The JSON content.

        Returns:
            None.

        Raises:
            None.
        """
        text = json.dumps(content, separators=(',', ':'), allow_nan=False)
        (self.target / f'{name}.json').write_text(text)

    def rounded(self, series: pd.Series) -> list:
        """Rounds a series to six decimals, with null for gaps.

        Args:
            series: The values.

        Returns:
            A list of floats and None.

        Raises:
            None.
        """
        values = []
        for value in series.to_numpy():
            if pd.isna(value):
                values.append(None)
            else:
                values.append(round(float(value), 6))
        return values

    def returns(self) -> dict:
        """Builds the monthly return series of every strategy.

        Args:
            None.

        Returns:
            A dictionary with the months, the benchmark and one entry per
            strategy.

        Raises:
            None.
        """
        raw = pd.read_parquet(
            self.data_folder / 'derived' / 'strategy_series.parquet'
        )
        raw.index = pd.PeriodIndex(raw.index, freq='M')
        window = raw.loc[StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST]
        benchmark = BenchmarkSeries(
            self.data_folder / 'nse' / 'nifty500_tri.json'
        ).monthly_returns()
        benchmark = benchmark.reindex(window.index)
        strategies = {}
        for universe in ('A', 'B'):
            for gap in ('noskip', 'skip'):
                for ranking in StudySettings.RANKING_MONTHS:
                    for holding in StudySettings.HOLDING_MONTHS:
                        stem = f'{universe}_{gap}_{ranking}_{holding}'
                        entry = {}
                        for key, suffix in self.SERIES:
                            entry[key] = self.rounded(
                                window[f'{stem}_{suffix}']
                            )
                        strategies[stem] = entry
        return {
            'months': [str(month) for month in window.index],
            'benchmark': self.rounded(benchmark),
            'strategies': strategies,
        }

    def tables(self) -> dict:
        """Collects the results tables and the paper's numbers.

        Args:
            None.

        Returns:
            A dictionary of tables as lists of records, with the paper's
            Table I and the other paper figures.

        Raises:
            None.
        """
        content = {}
        for name in self.TABLES:
            table = pd.read_csv(self.results / f'{name}.csv')
            table = table.round(6)
            table = table.astype(object).where(table.notna(), None)
            content[name] = table.to_dict(orient='records')
        paper = pd.read_csv(self.paper / 'paper_table_i.csv')
        content['paper_table_i'] = paper.to_dict(orient='records')
        content['paper_numbers'] = {
            'table_ii_beta': PaperNumbers.TABLE_II_BETA_ALL,
            'table_vii_cumulative_all': PaperNumbers.TABLE_VII_CUMULATIVE_ALL,
            'table_ix_all': PaperNumbers.TABLE_IX_ALL,
            'table_iii_all_p10_p1': PaperNumbers.TABLE_III_ALL_P10_P1,
            'table_iv': PaperNumbers.TABLE_IV,
            'table_vi': PaperNumbers.TABLE_VI,
            'table_vii_cumulative': {
                str(key): value
                for key, value in PaperNumbers.TABLE_VII_CUMULATIVE.items()
            },
            'table_ix_first_six_months': PaperNumbers.TABLE_IX_FIRST_SIX_MONTHS,
            'table_ix_months_11_to_18': PaperNumbers.TABLE_IX_MONTHS_11_TO_18,
            'section_iii': PaperNumbers.SECTION_III,
        }
        return content

    def meta(self, returns: dict) -> dict:
        """Describes the sample and the headline numbers.

        Args:
            returns: The dictionary from returns.

        Returns:
            A dictionary with dates and the headline strategy's numbers.

        Raises:
            None.
        """
        headline = pd.read_csv(self.results / 'headline_strategies.csv')
        pick = headline[
            (headline['universe'] == 'B')
            & (headline['strategy'] == 'long-only winners')
            & (headline['impact_cost'].round(4) == 0.001)
        ].iloc[0]
        return {
            'generated': datetime.date.today().isoformat(),
            'first_month': returns['months'][0],
            'last_month': returns['months'][-1],
            'months': len(returns['months']),
            'headline_cagr': round(float(pick['net_cagr']), 4),
            'benchmark_cagr': round(float(pick['benchmark_cagr']), 4),
            'headline_drawdown': round(float(pick['max_drawdown']), 4),
        }
