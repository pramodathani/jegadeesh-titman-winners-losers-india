"""Scholes-Williams betas from daily returns."""

import numpy as np
import pandas as pd


class ScholesWilliamsBetas:
    """Estimates each share's beta in each calendar year.

    Attributes:
        minimum_days: The fewest days with returns for an estimate.
    """

    def __init__(self, minimum_days: int = 100) -> None:
        """Sets the smallest sample.

        Args:
            minimum_days: The fewest days with returns for an estimate.

        Returns:
            None.

        Raises:
            None.
        """
        self.minimum_days = minimum_days

    def estimate(
        self,
        daily_returns: pd.DataFrame,
        market_returns: pd.Series,
    ) -> pd.DataFrame:
        """Estimates betas year by year.

        The beta is the sum of the slopes on the market return one day
        earlier, the same day and one day later, divided by one plus twice the
        market's first order autocorrelation.

        Args:
            daily_returns: Returns, sessions by shares.
            market_returns: The market's return on the same sessions.

        Returns:
            Betas, years by shares, NaN with fewer than minimum_days days.

        Raises:
            None.
        """
        market = market_returns.reindex(daily_returns.index)
        years = sorted(set(daily_returns.index.year))
        rows = []
        for year in years:
            inside = daily_returns.index.year == year
            rows.append(
                self._year(
                    daily_returns.loc[inside].to_numpy(),
                    market.loc[inside].to_numpy(),
                )
            )
        return pd.DataFrame(rows, index=years, columns=daily_returns.columns)

    def _year(self, shares: np.ndarray, market: np.ndarray) -> np.ndarray:
        """Estimates betas for one year.

        Args:
            shares: Returns, days by shares.
            market: The market's returns by day.

        Returns:
            One beta per share.

        Raises:
            None.
        """
        slopes = []
        for lag in (-1, 0, 1):
            shifted = np.roll(market, -lag)
            if lag == -1:
                shifted[0] = np.nan
            if lag == 1:
                shifted[-1] = np.nan
            slopes.append(self._slope(shares, shifted))
        both = ~np.isnan(market[1:]) & ~np.isnan(market[:-1])
        if both.sum() < 3:
            return np.full(shares.shape[1], np.nan)
        correlation = np.corrcoef(market[1:][both], market[:-1][both])[0, 1]
        return (slopes[0] + slopes[1] + slopes[2]) / (1.0 + 2.0 * correlation)

    def _slope(self, shares: np.ndarray, market: np.ndarray) -> np.ndarray:
        """Regresses each share's returns on a market series.

        Args:
            shares: Returns, days by shares.
            market: The market series, same length, NaN where missing.

        Returns:
            The slope per share, NaN with too few days.

        Raises:
            None.
        """
        valid = ~np.isnan(shares) & ~np.isnan(market)[:, None]
        count = valid.sum(axis=0)
        x_values = np.where(valid, market[:, None], 0.0)
        y_values = np.where(valid, shares, 0.0)
        with np.errstate(divide='ignore', invalid='ignore'):
            mean_x = x_values.sum(axis=0) / count
            mean_y = y_values.sum(axis=0) / count
            covariance = (x_values * y_values).sum(axis=0) / count
            covariance = covariance - mean_x * mean_y
            variance = (x_values * x_values).sum(axis=0) / count
            variance = variance - mean_x * mean_x
            slope = covariance / variance
        slope[count < self.minimum_days] = np.nan
        return slope
