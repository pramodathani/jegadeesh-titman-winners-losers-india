"""The skipped week implemented by ending the ranking window earlier."""

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.ranking import PastReturnRanker
from jegadeesh_titman_india.momentum.relative_strength import (
    RelativeStrengthStrategy,
)
from jegadeesh_titman_india.momentum.study_inputs import StudyInputs
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class EarlierRankingSkip:
    """Ranks on returns that end a week before the month end.

    The main study leaves its gap by holding from five sessions after a
    month-end ranking. This variant ranks on a window that ends five sessions
    before the month end and holds calendar months, so the gap is the last
    week of the ranking month. Both leave five sessions between the end of
    the ranking window and the first day of holding.

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

    def table(self) -> pd.DataFrame:
        """Gives the buy-minus-sell mean for all 16 strategies per universe.

        Args:
            None.

        Returns:
            One row per universe, J and K with the mean monthly return before
            costs and its ordinary t-statistic over the main sample.

        Raises:
            None.
        """
        statistics = ReturnStatistics()
        rows = []
        for universe, mask in (
            ('A', self.inputs.universe_a),
            ('B', self.inputs.universe_b),
        ):
            for ranking_months in StudySettings.RANKING_MONTHS:
                ranker = PastReturnRanker(ranking_months)
                past = ranker.past_returns(self.inputs.earlier_returns)
                deciles = ranker.deciles(past, mask)
                for holding_months in StudySettings.HOLDING_MONTHS:
                    strategy = RelativeStrengthStrategy(
                        deciles,
                        holding_months,
                        self.inputs.standard_returns,
                    )
                    result = strategy.run(strategy.long_short_weights(), None)
                    series = (
                        result['gross_return']
                        .loc[StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST]
                        .dropna()
                    )
                    mean, t_statistic = statistics.mean_and_t(series)
                    rows.append(
                        {
                            'universe': universe,
                            'J': ranking_months,
                            'K': holding_months,
                            'mean': mean,
                            't_ols': t_statistic,
                            'months': len(series),
                        }
                    )
        return pd.DataFrame(rows)
