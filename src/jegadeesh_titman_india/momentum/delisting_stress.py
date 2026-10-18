"""A stress test for shares that disappear without a final return."""

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics

from jegadeesh_titman_india.momentum.relative_strength import (
    RelativeStrengthStrategy,
)
from jegadeesh_titman_india.momentum.study_settings import StudySettings


class DelistingStress:
    """Charges a loss in the month after a share's last return.

    The bhavcopies give a share's last traded close but not what holders got
    when it was delisted, so the base results charge nothing after the last
    trade. This test charges a chosen loss, an extreme bound because many
    exits are mergers or symbol changes, to see how much it could matter.

    Attributes:
        loss: The return charged in the month after the last return.
        minimum_months_absent: How many months a share must be gone for the
            end of its returns to count as an exit.
    """

    def __init__(
        self,
        loss: float = -1.0,
        minimum_months_absent: int = 2,
    ) -> None:
        """Sets the loss and the absence needed.

        Args:
            loss: The return charged after the last return.
            minimum_months_absent: Months without returns at the end.

        Returns:
            None.

        Raises:
            None.
        """
        self.loss = loss
        self.minimum_months_absent = minimum_months_absent

    def stressed_returns(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Inserts the loss in the month after each exiting share's last return.

        Args:
            returns: Monthly returns, months by shares.

        Returns:
            A copy of the returns with the loss inserted.

        Raises:
            None.
        """
        stressed = returns.copy()
        valid = returns.notna()
        has_any = valid.any(axis=0)
        last_label = valid.iloc[::-1].idxmax()
        positions = {month: place for place, month in enumerate(returns.index)}
        final = len(returns.index) - 1
        for symbol in returns.columns[has_any]:
            place = positions[last_label[symbol]]
            if final - place >= self.minimum_months_absent:
                stressed.iloc[place + 1, stressed.columns.get_loc(symbol)] = (
                    self.loss
                )
        return stressed

    def table(
        self,
        deciles: pd.DataFrame,
        holding_months: int,
        returns: pd.DataFrame,
        universe: str,
    ) -> pd.DataFrame:
        """Gives the long-short return under four treatments of exits.

        Args:
            deciles: Decile numbers at the end of each month.
            holding_months: K.
            returns: Monthly returns used for holding.
            universe: A or B, for the label.

        Returns:
            One row per treatment: none, both legs, losers only and winners
            only, with the mean monthly return and its t-statistics.

        Raises:
            None.
        """
        base = RelativeStrengthStrategy(deciles, holding_months, returns)
        harsh = RelativeStrengthStrategy(
            deciles,
            holding_months,
            self.stressed_returns(returns),
        )
        legs = {
            'buy': {
                'none': base,
                'both legs': harsh,
                'losers only': base,
                'winners only': harsh,
            },
            'sell': {
                'none': base,
                'both legs': harsh,
                'losers only': harsh,
                'winners only': base,
            },
        }
        statistics = ReturnStatistics()
        rows = []
        for treatment in legs['buy']:
            buy = legs['buy'][treatment]
            sell = legs['sell'][treatment]
            weights = buy.weights(10)
            buy_return = buy.run(weights, None)['gross_return']
            weights = sell.weights(1)
            sell_return = sell.run(weights, None)['gross_return']
            spread = buy_return - sell_return
            sample = spread.loc[
                StudySettings.MAIN_FIRST : StudySettings.MAIN_LAST
            ]
            sample = sample.dropna()
            mean, t_statistic = statistics.mean_and_t(sample)
            _, nw_t = statistics.newey_west_mean_and_t(sample)
            rows.append(
                {
                    'universe': universe,
                    'treatment': treatment,
                    'mean': mean,
                    't_ols': t_statistic,
                    't_nw': nw_t,
                    'months': len(sample),
                }
            )
        return pd.DataFrame(rows)
