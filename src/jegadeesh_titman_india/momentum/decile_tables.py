"""Tables II and III: decile portfolios, betas, size and subsamples."""

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.ranking import PastReturnRanker
from jegadeesh_titman_india.momentum.relative_strength import (
    RelativeStrengthStrategy,
)
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings
from jegadeesh_titman_india.momentum.subsamples import Subsamples


class DecileTables:
    """The 6-month/6-month deciles of Tables II and III.

    Attributes:
        inputs: The study inputs.
        ranking_months: J.
        holding_months: K.
    """

    def __init__(
        self,
        inputs: StudyInputs,
        ranking_months: int = 6,
        holding_months: int = 6,
    ) -> None:
        """Keeps the inputs and the strategy's J and K.

        Args:
            inputs: The loaded study inputs.
            ranking_months: J.
            holding_months: K.

        Returns:
            None.

        Raises:
            None.
        """
        self.inputs = inputs
        self.ranking_months = ranking_months
        self.holding_months = holding_months
        self.statistics = ReturnStatistics()

    def mask(self, universe: str) -> pd.DataFrame:
        """Gives a universe's eligibility table.

        Args:
            universe: A or B.

        Returns:
            Bools, months by shares.

        Raises:
            None.
        """
        if universe == 'A':
            return self.inputs.universe_a
        return self.inputs.universe_b

    def strategy(
        self,
        mask: pd.DataFrame,
        minimum_shares: int,
    ) -> RelativeStrengthStrategy:
        """Builds the strategy on a set of eligible shares.

        Args:
            mask: Bools, months by shares.
            minimum_shares: The fewest ranked shares for a month to count.

        Returns:
            The strategy, with no skipped week.

        Raises:
            None.
        """
        ranker = PastReturnRanker(self.ranking_months, minimum_shares)
        past = ranker.past_returns(self.inputs.standard_returns)
        deciles = ranker.deciles(past, mask)
        return RelativeStrengthStrategy(
            deciles,
            self.holding_months,
            self.inputs.standard_returns,
        )

    def decile_returns(
        self,
        strategy: RelativeStrengthStrategy,
    ) -> pd.DataFrame:
        """Gives each decile portfolio's monthly return before costs.

        Args:
            strategy: The strategy.

        Returns:
            A table with columns 1 to 10 and P10-P1, months by portfolios.

        Raises:
            None.
        """
        columns = {}
        for decile in range(1, 11):
            weights = strategy.weights(decile)
            result = strategy.run(weights, None)
            columns[decile] = result['gross_return']
        table = pd.DataFrame(columns)
        table['P10-P1'] = table[10] - table[1]
        return table

    def score(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Gives each portfolio's mean, t-statistic and alpha.

        The alpha regresses excess returns on the NIFTY 500 total return's
        excess return, over the months that have a risk-free rate.

        Args:
            returns: Monthly returns by portfolio.

        Returns:
            One row per portfolio with mean, t, months, alpha, alpha_t, beta
            and alpha_months.

        Raises:
            None.
        """
        main = returns.loc[StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST]
        market = self.inputs.market_monthly.reindex(main.index)
        risk_free = self.inputs.risk_free.reindex(main.index)
        rows = []
        for name in main.columns:
            series = main[name].dropna()
            mean, t_statistic = self.statistics.mean_and_t(series)
            zero_cost = name == 'P10-P1'
            offset = 0.0 if zero_cost else risk_free
            excess = (main[name] - offset).dropna()
            market_excess = market - risk_free
            model = self.statistics.market_model(
                excess.dropna(),
                market_excess.dropna(),
            )
            rows.append(
                {
                    'portfolio': name,
                    'mean': mean,
                    't': t_statistic,
                    'months': len(series),
                    'alpha': model['alpha'],
                    'alpha_t': model['alpha_t'],
                    'beta': model['beta'],
                    'alpha_months': model['periods'],
                }
            )
        return pd.DataFrame(rows)

    def subsample_masks(self, universe: str) -> dict[str, pd.DataFrame]:
        """Builds the eligibility tables of every subsample of a universe.

        Args:
            universe: A or B.

        Returns:
            A dictionary from All, S1 to S3 and B1 to B3 to a bool table.

        Raises:
            None.
        """
        base = self.mask(universe)
        splitter = Subsamples()
        subsamples = {'All': base}
        sizes = splitter.size_terciles(self.inputs.median_values, base)
        betas = splitter.beta_terciles(self.inputs.betas, base)
        for third, mask in sizes.items():
            subsamples[f'S{third}'] = mask
        for third, mask in betas.items():
            subsamples[f'B{third}'] = mask
        return subsamples

    def table_three(self, universe: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Runs the 6/6 deciles on every subsample of a universe.

        Args:
            universe: A or B.

        Returns:
            A pair. The first has the scores of every decile with a column
            for the subsample. The second holds the monthly P10-P1 return of
            each subsample, months by subsamples.

        Raises:
            None.
        """
        frames = []
        zero_cost = {}
        for name, mask in self.subsample_masks(universe).items():
            minimum = 100 if name == 'All' else 30
            strategy = self.strategy(mask, minimum)
            returns = self.decile_returns(strategy)
            zero_cost[name] = returns['P10-P1']
            scored = self.score(returns)
            scored.insert(0, 'subsample', name)
            frames.append(scored)
        table = pd.concat(frames, ignore_index=True)
        table.insert(0, 'universe', universe)
        return table, pd.DataFrame(zero_cost)

    def table_two(self, universe: str) -> pd.DataFrame:
        """Gives each decile's beta and average size proxy.

        Args:
            universe: A or B.

        Returns:
            One row per decile with beta and the average median daily traded
            value of its members at formation, in crore rupees.

        Raises:
            None.
        """
        strategy = self.strategy(self.mask(universe), 100)
        scored = self.score(self.decile_returns(strategy))
        sample = strategy.deciles.loc[
            StudySettings.MAIN_FIRST - 1 : StudySettings.MAIN_LAST
        ]
        values = self.inputs.median_values.reindex_like(sample)
        sizes = {}
        for decile in range(1, 11):
            members = sample == decile
            per_month = values.where(members).mean(axis=1)
            sizes[str(decile)] = per_month.mean() / 1e7
        rows = []
        for name in [str(number) for number in range(1, 11)] + ['P10-P1']:
            key = int(name) if name.isdigit() else name
            beta = scored.loc[scored['portfolio'] == key, 'beta'].iloc[0]
            rows.append(
                {
                    'universe': universe,
                    'portfolio': name,
                    'beta': beta,
                    'median_traded_value_crore': sizes.get(name),
                }
            )
        return pd.DataFrame(rows)
