"""Runs the 32 J/K strategies of Table I on each universe."""

import pandas as pd
from brahmagupta.costs.delivery_costs import DeliveryCosts
from brahmagupta.performance_report import PerformanceReport

from jegadeesh_titman_india.momentum.ranking import PastReturnRanker
from jegadeesh_titman_india.momentum.relative_strength import (
    RelativeStrengthStrategy,
)
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class StrategyGrid:
    """All J/K strategies, with and without the skipped week.

    Attributes:
        inputs: The study inputs.
        series: Monthly return series of every strategy, by column name.
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
        self.series: dict[str, pd.Series] = {}

    def universe_mask(self, universe: str) -> pd.DataFrame:
        """Gives the eligibility table of a universe.

        Args:
            universe: A or B.

        Returns:
            Bools, months by shares.

        Raises:
            ValueError: When the universe is not A or B.
        """
        if universe == 'A':
            return self.inputs.universe_a
        if universe == 'B':
            return self.inputs.universe_b
        raise ValueError(f'Unknown universe {universe}')

    def strategy(
        self,
        universe: str,
        skip: bool,
        ranking_months: int,
        holding_months: int,
    ) -> RelativeStrengthStrategy:
        """Builds one strategy.

        Args:
            universe: A or B.
            skip: Whether to skip a week between ranking and holding.
            ranking_months: J.
            holding_months: K.

        Returns:
            The strategy.

        Raises:
            None.
        """
        ranker = PastReturnRanker(ranking_months)
        past = ranker.past_returns(self.inputs.standard_returns)
        deciles = ranker.deciles(past, self.universe_mask(universe))
        returns = self.inputs.standard_returns
        if skip:
            returns = self.inputs.shifted_returns
        return RelativeStrengthStrategy(deciles, holding_months, returns)

    def run(self) -> pd.DataFrame:
        """Runs every strategy and summarises it over the main sample.

        Args:
            None.

        Returns:
            One row per universe, skip, J and K.

        Raises:
            None.
        """
        rows = []
        for universe in ('A', 'B'):
            for skip in (False, True):
                for ranking_months in StudySettings.RANKING_MONTHS:
                    for holding_months in StudySettings.HOLDING_MONTHS:
                        rows.append(
                            self._one(
                                universe,
                                skip,
                                ranking_months,
                                holding_months,
                            )
                        )
        return pd.DataFrame(rows)

    def _one(
        self,
        universe: str,
        skip: bool,
        ranking_months: int,
        holding_months: int,
    ) -> dict:
        """Runs one strategy and scores its legs.

        Args:
            universe: A or B.
            skip: Whether to skip a week.
            ranking_months: J.
            holding_months: K.

        Returns:
            A row of results.

        Raises:
            None.
        """
        strategy = self.strategy(universe, skip, ranking_months, holding_months)
        costs = DeliveryCosts(StudySettings.IMPACT_COST[universe])
        buy_weights = strategy.weights(10)
        sell_weights = strategy.weights(1)
        buy = strategy.run(buy_weights, costs)
        sell = strategy.run(sell_weights, costs)
        both = strategy.run(buy_weights - sell_weights, costs)
        name = f'{universe}_{"skip" if skip else "noskip"}_{ranking_months}_{holding_months}'
        self.series[f'{name}_sell_gross'] = sell['gross_return']
        self.series[f'{name}_buy_gross'] = buy['gross_return']
        self.series[f'{name}_bs_gross'] = both['gross_return']
        self.series[f'{name}_bs_net'] = both['net_return']
        self.series[f'{name}_buy_net'] = buy['net_return']
        self.series[f'{name}_bs_turnover'] = both['turnover']
        self.series[f'{name}_buy_turnover'] = buy['turnover']
        row = {
            'universe': universe,
            'skip': skip,
            'J': ranking_months,
            'K': holding_months,
        }
        row.update(self._score('sell', sell['gross_return'], None))
        row.update(self._score('buy', buy['gross_return'], None))
        row.update(self._score('bs', both['gross_return'], None))
        row.update(self._score('bs_net', both['net_return'], None))
        benchmark = self.inputs.market_monthly
        row.update(self._score('lo_net', buy['net_return'], benchmark))
        row['bs_turnover'] = self._main(both['turnover']).mean()
        row['lo_turnover'] = self._main(buy['turnover']).mean()
        return row

    def _main(self, series: pd.Series) -> pd.Series:
        """Restricts a series to the main sample and drops gaps.

        Args:
            series: A monthly series.

        Returns:
            The series over the main sample.

        Raises:
            None.
        """
        window = series.loc[StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST]
        return window.dropna()

    def _score(
        self,
        prefix: str,
        returns: pd.Series,
        benchmark: pd.Series | None,
    ) -> dict:
        """Scores a series over the main sample.

        Args:
            prefix: The start of each column name.
            returns: Monthly returns.
            benchmark: A benchmark's monthly returns, or None.

        Returns:
            A dictionary of named statistics.

        Raises:
            None.
        """
        sample = self._main(returns)
        report = PerformanceReport(sample, benchmark).summary()
        scores = {
            f'{prefix}_mean': report['mean'],
            f'{prefix}_t_ols': report['t_statistic'],
            f'{prefix}_t_nw': report['newey_west_t'],
            f'{prefix}_months': report['periods'],
            f'{prefix}_cagr': report['compound_annual'],
            f'{prefix}_max_drawdown': report['maximum_drawdown'],
        }
        if benchmark is not None:
            scores[f'{prefix}_excess_annual'] = report['excess_annual']
            scores[f'{prefix}_excess_mean'] = report['excess_mean']
            scores[f'{prefix}_excess_t'] = report['excess_t']
            scores[f'{prefix}_alpha'] = report['alpha']
            scores[f'{prefix}_beta'] = report['beta']
            scores['benchmark_cagr'] = report['benchmark_compound_annual']
        return scores
