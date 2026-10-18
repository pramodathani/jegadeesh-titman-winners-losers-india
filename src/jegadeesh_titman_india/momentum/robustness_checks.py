"""Robustness checks on the 6/6 long-short and long-only strategies."""

import copy

import pandas as pd
from brahmagupta.costs.delivery_costs import DeliveryCosts
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.strategy_grid import StrategyGrid
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class RobustnessChecks:
    """Re-runs the headline strategy under changed data or samples.

    Attributes:
        inputs: The study inputs.
    """

    def __init__(self, inputs: StudyInputs) -> None:
        """Keeps the inputs.

        Args:
            inputs: The loaded study inputs.

        Returns:
            None.

        Raises:
            None.
        """
        self.inputs = inputs

    def changed_inputs(self, variant: str) -> StudyInputs:
        """Builds a copy of the inputs for a data variant.

        Args:
            variant: base, no_big_winners or winsorised.

        Returns:
            The inputs, shallow copied with tables replaced.

        Raises:
            None.
        """
        changed = copy.copy(self.inputs)
        if variant == 'no big winners':
            maximum = self.inputs.standard_returns.max(axis=0)
            keep = maximum <= 3.0
            changed.universe_a = self.inputs.universe_a & keep
            changed.universe_b = self.inputs.universe_b & keep
        if variant == 'winsorised at +100%':
            changed.standard_returns = self.inputs.standard_returns.clip(
                upper=1.0
            )
            changed.shifted_returns = self.inputs.shifted_returns.clip(
                upper=1.0
            )
        return changed

    def table(self) -> pd.DataFrame:
        """Scores the 6/6 no-skip long-short portfolio under each variant.

        Args:
            None.

        Returns:
            One row per universe and variant.

        Raises:
            None.
        """
        statistics = ReturnStatistics()
        rows = []
        ranking = StudySettings.HEADLINE_RANKING
        holding = StudySettings.HEADLINE_HOLDING
        variants = [
            ('base', 'base', None),
            ('excluding 2009', 'base', 'ex2009'),
            ('excluding March', 'base', 'exMarch'),
            ('excluding January', 'base', 'exJanuary'),
            ('no big winners', 'no big winners', None),
            ('winsorised at +100%', 'winsorised at +100%', None),
        ]
        for universe in ('A', 'B'):
            for label, data_variant, months in variants:
                grid = StrategyGrid(self.changed_inputs(data_variant))
                strategy = grid.strategy(universe, False, ranking, holding)
                weights = strategy.long_short_weights()
                impact = StudySettings.IMPACT_COST[universe]
                for multiple in (1, 2):
                    costs = DeliveryCosts(impact * multiple)
                    result = strategy.run(weights, costs)
                    for column in ('gross_return', 'net_return'):
                        if multiple == 2 and column == 'gross_return':
                            continue
                        series = result[column].loc[
                            StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST
                        ]
                        series = self._drop(series, months).dropna()
                        mean, t_statistic = statistics.mean_and_t(series)
                        _, nw_t = statistics.newey_west_mean_and_t(series)
                        kind = column.removesuffix('_return')
                        if multiple == 2:
                            kind = 'net at double impact'
                        rows.append(
                            {
                                'universe': universe,
                                'variant': label,
                                'return': kind,
                                'mean': mean,
                                't_ols': t_statistic,
                                't_nw': nw_t,
                                'months': len(series),
                            }
                        )
        return pd.DataFrame(rows)

    def _drop(self, series: pd.Series, months: str | None) -> pd.Series:
        """Removes some months from a series.

        Args:
            series: A monthly series.
            months: None, ex2009, exMarch or exJanuary.

        Returns:
            The series without those months.

        Raises:
            None.
        """
        if months == 'ex2009':
            return series[series.index.year != 2009]
        if months == 'exMarch':
            return series[series.index.month != 3]
        if months == 'exJanuary':
            return series[series.index.month != 1]
        return series
