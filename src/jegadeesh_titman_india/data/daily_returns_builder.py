"""Builds daily total returns for every NSE share from bhavcopies."""

import numpy as np
import pandas as pd


class DailyReturnsBuilder:
    """Adjusts bhavcopy closes for corporate actions and computes returns.

    Attributes:
        lowest_return: Returns below this are treated as data errors.
        highest_return: Returns above this are treated as data errors.
    """

    def __init__(
        self,
        lowest_return: float = -0.5,
        highest_return: float = 1.0,
    ) -> None:
        """Sets the limits for data errors.

        Args:
            lowest_return: The lowest believable one-day return.
            highest_return: The highest believable one-day return.

        Returns:
            None.

        Raises:
            None.
        """
        self.lowest_return = lowest_return
        self.highest_return = highest_return

    def build(
        self,
        prices: pd.DataFrame,
        actions: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Computes each share's daily return.

        The return on a trading day is (close times the price factor of any
        actions that went ex since the share's previous trade, plus their
        dividends) divided by the previous close, minus one. An action whose
        ex-date is not a trading day applies on the first trading day after.

        Args:
            prices: Columns date, symbol, series, close and traded_value.
            actions: Columns symbol, ex_date, factor and dividend.

        Returns:
            A pair. The first table has columns date, symbol, series, close,
            traded_value, factor, dividend and ret. The second lists the
            returns that were set to zero as data errors, with columns
            date, symbol, raw_return, factor and dividend.

        Raises:
            None.
        """
        table = prices.sort_values(['symbol', 'date']).reset_index(drop=True)
        table['factor'] = 1.0
        table['dividend'] = 0.0
        self._attach_actions(table, actions)
        previous_close = table.groupby('symbol')['close'].shift(1)
        adjusted = table['close'] * table['factor'] + table['dividend']
        table['ret'] = adjusted / previous_close - 1.0
        too_low = table['ret'] < self.lowest_return
        too_high = table['ret'] > self.highest_return
        errors = table.loc[
            too_low | too_high,
            ['date', 'symbol', 'ret', 'factor', 'dividend'],
        ].rename(columns={'ret': 'raw_return'})
        table.loc[too_low | too_high, 'ret'] = 0.0
        return table, errors.reset_index(drop=True)

    def _attach_actions(
        self,
        table: pd.DataFrame,
        actions: pd.DataFrame,
    ) -> None:
        """Writes each action's factor and dividend onto its trading day.

        Args:
            table: The price table sorted by symbol and date; changed in
                place.
            actions: The corporate actions.

        Returns:
            None.

        Raises:
            None.
        """
        if len(actions) == 0:
            return
        starts = table.groupby('symbol').indices
        dates = table['date'].to_numpy()
        factors = table['factor'].to_numpy().copy()
        dividends = table['dividend'].to_numpy().copy()
        for action in actions.itertuples(index=False):
            positions = starts.get(action.symbol)
            if positions is None:
                continue
            symbol_dates = dates[positions]
            first = int(
                np.searchsorted(symbol_dates, np.datetime64(action.ex_date))
            )
            if first == 0 or first >= len(positions):
                continue
            row = positions[first]
            factors[row] *= action.factor
            dividends[row] += action.dividend
        table['factor'] = factors
        table['dividend'] = dividends
