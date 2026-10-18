"""Builds and caches the monthly inputs every table of the study uses."""

import pathlib

import pandas as pd

from jegadeesh_titman_india.data.benchmark_series import (
    BenchmarkSeries,
    IimaFactors,
)
from jegadeesh_titman_india.momentum.market_panels import MarketPanels
from jegadeesh_titman_india.momentum.scholes_williams import (
    ScholesWilliamsBetas,
)
from jegadeesh_titman_india.momentum.universes import UniverseBuilder


class StudyInputs:
    """Monthly returns, universes, betas and benchmark series.

    Attributes:
        standard_returns: Calendar month returns, months by shares.
        shifted_returns: Returns of months that start after the skip.
        earlier_returns: Returns of months that end before the month end.
        universe_a: Bools, months by shares, for universe A.
        universe_b: Bools, months by shares, for universe B.
        median_values: Median daily traded value, months by shares.
        trading_shares: Share of sessions traded, months by shares.
        betas: Scholes-Williams betas, years by shares.
        market_monthly: NIFTY 500 total return by month.
        risk_free: Risk-free return by month, NaN after December 2025.
        wml_iima: The IIMA winner-minus-loser factor by month.
    """

    NAMES: tuple[str, ...] = (
        'standard_returns',
        'shifted_returns',
        'earlier_returns',
        'universe_a',
        'universe_b',
        'median_values',
        'trading_shares',
    )

    def __init__(self, data_folder: pathlib.Path) -> None:
        """Remembers where the data is.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.cache_folder = data_folder / 'derived' / 'inputs'

    def build(self, last_month: pd.Period) -> None:
        """Builds every input from the daily returns and saves it.

        Args:
            last_month: The last complete month.

        Returns:
            None.

        Raises:
            None.
        """
        daily = pd.read_parquet(
            self.data_folder / 'derived' / 'daily_returns.parquet',
            columns=['date', 'symbol', 'traded_value', 'ret'],
        )
        panels = MarketPanels(daily, last_month)
        del daily
        standard = panels.standard_returns()
        shifted = panels.shifted_returns().reindex(
            index=standard.index,
            columns=standard.columns,
        )
        earlier = panels.earlier_returns().reindex(
            index=standard.index,
            columns=standard.columns,
        )
        builder = UniverseBuilder(panels)
        universe_a = builder.universe_a(standard)
        medians, shares = builder.liquidity()
        universe_b = builder.universe_b(universe_a, medians, shares)
        benchmark = BenchmarkSeries(
            self.data_folder / 'nse' / 'nifty500_tri.json'
        )
        market_daily = benchmark.daily_returns(panels.sessions)
        betas = ScholesWilliamsBetas().estimate(
            panels.daily_returns,
            market_daily,
        )
        self.cache_folder.mkdir(parents=True, exist_ok=True)
        tables = {
            'standard_returns': standard,
            'shifted_returns': shifted,
            'earlier_returns': earlier,
            'universe_a': universe_a,
            'universe_b': universe_b,
            'median_values': medians,
            'trading_shares': shares,
        }
        for name, table in tables.items():
            saved = table.copy()
            saved.index = saved.index.astype(str)
            saved.to_parquet(self.cache_folder / f'{name}.parquet')
        betas.columns = betas.columns.astype(str)
        betas.index = betas.index.astype(str)
        betas.to_parquet(self.cache_folder / 'betas.parquet')
        market_daily.rename('ret').to_frame().to_parquet(
            self.cache_folder / 'market_daily.parquet'
        )

    def load(self) -> None:
        """Loads the cached inputs and the benchmark series.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        for name in self.NAMES:
            table = pd.read_parquet(self.cache_folder / f'{name}.parquet')
            table.index = pd.PeriodIndex(table.index, freq='M')
            setattr(self, name, table)
        betas = pd.read_parquet(self.cache_folder / 'betas.parquet')
        betas.index = betas.index.astype(int)
        self.betas = betas
        market = pd.read_parquet(self.cache_folder / 'market_daily.parquet')
        self.market_daily = market['ret']
        benchmark = BenchmarkSeries(
            self.data_folder / 'nse' / 'nifty500_tri.json'
        )
        self.market_monthly = benchmark.monthly_returns()
        factors = IimaFactors(
            next((self.data_folder / 'nse' / 'iima').glob('*.csv'))
        )
        self.risk_free = factors.table['RF']
        self.wml_iima = factors.table['WML']
