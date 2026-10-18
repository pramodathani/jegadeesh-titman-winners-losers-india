"""The headline long-only and long-short strategies, with cost sensitivity."""

import pandas as pd
from brahmagupta.costs.delivery_costs import DeliveryCosts
from brahmagupta.performance_report import PerformanceReport
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.strategy_grid import StrategyGrid
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class HeadlineStrategies:
    """The 6/6 strategy without a skipped week, fixed before the results.

    Attributes:
        inputs: The study inputs.
        grid: The strategy grid used to build strategies.
    """

    IMPACT_COSTS: tuple[float, ...] = (0.0, 0.001, 0.002, 0.003)

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
        self.grid = StrategyGrid(inputs)

    def table(self) -> pd.DataFrame:
        """Scores the headline strategies at several impact costs.

        Args:
            None.

        Returns:
            One row per strategy and impact cost. The long-only rows score
            the winners decile against the NIFTY 500 total return.

        Raises:
            None.
        """
        rows = []
        ranking = StudySettings.HEADLINE_RANKING
        holding = StudySettings.HEADLINE_HOLDING
        for universe in ('A', 'B'):
            strategy = self.grid.strategy(universe, False, ranking, holding)
            winners = strategy.weights(10)
            losers = strategy.weights(1)
            portfolios = {
                'long-only winners': winners,
                'long-short': winners - losers,
            }
            for name, weights in portfolios.items():
                for impact in self.IMPACT_COSTS:
                    result = strategy.run(weights, DeliveryCosts(impact))
                    rows.append(self._row(universe, name, impact, result))
        return pd.DataFrame(rows)

    def _row(
        self,
        universe: str,
        name: str,
        impact: float,
        result: pd.DataFrame,
    ) -> dict:
        """Scores one run.

        Args:
            universe: A or B.
            name: The strategy's name.
            impact: The impact cost per side.
            result: The backtest table.

        Returns:
            A dictionary of results.

        Raises:
            None.
        """
        first = StudySettings.MAIN_FIRST
        last = StudySettings.MAIN_LAST
        net = result['net_return'].loc[first:last].dropna()
        gross = result['gross_return'].loc[first:last].dropna()
        benchmark = None
        if name == 'long-only winners':
            benchmark = self.inputs.market_monthly
        report = PerformanceReport(net, benchmark).summary()
        row = {
            'universe': universe,
            'strategy': name,
            'impact_cost': impact,
            'months': report['periods'],
            'gross_mean': gross.mean(),
            'net_mean': report['mean'],
            'net_t_ols': report['t_statistic'],
            'net_t_nw': report['newey_west_t'],
            'net_cagr': report['compound_annual'],
            'volatility': report['volatility_annual'],
            'max_drawdown': report['maximum_drawdown'],
            'turnover': result['turnover'].loc[first:last].mean(),
            'cost_per_month': result['costs'].loc[first:last].mean(),
        }
        if benchmark is not None:
            row['benchmark_cagr'] = report['benchmark_compound_annual']
            row['excess_annual'] = report['excess_annual']
            row['excess_t'] = report['excess_t']
            row.update(self._risk_adjusted(net))
        return row

    def _risk_adjusted(self, net: pd.Series) -> dict:
        """Gives the alpha over the risk-free rate and the market.

        Args:
            net: Net monthly returns.

        Returns:
            Alpha, its t-statistic, beta and months, over months with a
            risk-free rate.

        Raises:
            None.
        """
        market = self.inputs.market_monthly.reindex(net.index)
        risk_free = self.inputs.risk_free.reindex(net.index)
        model = ReturnStatistics().market_model(
            (net - risk_free).dropna(),
            (market - risk_free).dropna(),
        )
        return {
            'alpha_monthly': model['alpha'],
            'alpha_t': model['alpha_t'],
            'beta': model['beta'],
            'alpha_months': model['periods'],
        }
