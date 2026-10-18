"""Draws the wealth and drawdown chart of the headline strategies."""

import pathlib

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class WealthChart:
    """One rupee invested in January 2007, after costs.

    Attributes:
        data_folder: The study's data folder.
    """

    def __init__(self, data_folder: pathlib.Path) -> None:
        """Keeps the data folder.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder

    def draw(self, target: pathlib.Path, years: pathlib.Path) -> None:
        """Draws the chart and writes the year-end wealth.

        Args:
            target: The PNG file to write.
            years: The CSV file for year-end wealth.

        Returns:
            None.

        Raises:
            None.
        """
        inputs = StudyInputs(self.data_folder)
        inputs.load()
        series = pd.read_parquet(
            self.data_folder / 'derived' / 'strategy_series.parquet'
        )
        series.index = pd.PeriodIndex(series.index, freq='M')
        first = StudySettings.MAIN_FIRST
        last = StudySettings.MAIN_LAST
        curves = {
            'Winners decile, liquid 500, after costs': series[
                'B_noskip_6_6_buy_net'
            ],
            'NIFTY 500 total return': inputs.market_monthly,
            'Winners minus losers, liquid 500, after costs (paper portfolio)': series[
                'B_noskip_6_6_bs_net'
            ],
        }
        figure, axes = plt.subplots(
            2,
            1,
            figsize=(9, 7),
            sharex=True,
            gridspec_kw={'height_ratios': [3, 1.4]},
        )
        year_ends = {}
        for name, returns in curves.items():
            window = returns.loc[first:last].dropna()
            wealth = (1.0 + window).cumprod()
            year_ends[name] = wealth[wealth.index.month == 12]
            axes[0].plot(wealth.index.to_timestamp(), wealth, label=name)
            if 'minus' not in name:
                drawdown = wealth / wealth.cummax() - 1.0
                axes[1].plot(drawdown.index.to_timestamp(), drawdown * 100.0)
        axes[0].set_yscale('log')
        axes[0].set_ylabel('Value of 1 rupee (log scale)')
        axes[0].legend(loc='upper left', fontsize=8)
        axes[0].set_title('6-month ranking, 6-month holding, 2007-2026')
        axes[1].set_ylabel('Drawdown, %')
        axes[0].grid(alpha=0.3)
        axes[1].grid(alpha=0.3)
        target.parent.mkdir(parents=True, exist_ok=True)
        figure.tight_layout()
        figure.savefig(target, dpi=130)
        table = pd.DataFrame(year_ends)
        table.index = table.index.year
        table.index.name = 'year'
        table.columns = ['winners_long_only', 'nifty500_tri', 'long_short']
        table.to_csv(years)
