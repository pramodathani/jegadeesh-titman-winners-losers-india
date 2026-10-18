"""Splits a universe into size terciles and beta terciles."""

import numpy as np
import pandas as pd


class Subsamples:
    """Builds the S1 to S3 and B1 to B3 masks of Table III."""

    def terciles(
        self,
        values: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> dict[int, pd.DataFrame]:
        """Splits eligible shares into thirds by a measure each month.

        Args:
            values: The measure, months by shares.
            eligible: Bools, months by shares.

        Returns:
            A dictionary from 1 (lowest third) to 3 (highest third) to a bool
            table, months by shares.

        Raises:
            None.
        """
        usable = values.where(eligible.reindex_like(values) & values.notna())
        ranks = usable.rank(axis=1, method='first')
        counts = usable.notna().sum(axis=1)
        position = np.floor((ranks - 1.0).div(counts, axis=0) * 3.0) + 1.0
        return {third: position == third for third in (1, 2, 3)}

    def size_terciles(
        self,
        median_values: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> dict[int, pd.DataFrame]:
        """Splits by median daily traded value, the size proxy.

        Args:
            median_values: Median daily traded value, months by shares.
            eligible: Bools, months by shares.

        Returns:
            Terciles 1 (smallest) to 3 (largest).

        Raises:
            None.
        """
        return self.terciles(median_values, eligible)

    def beta_terciles(
        self,
        betas: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> dict[int, pd.DataFrame]:
        """Splits by the previous calendar year's Scholes-Williams beta.

        Args:
            betas: Betas, years by shares.
            eligible: Bools, months by shares.

        Returns:
            Terciles 1 (lowest beta) to 3 (highest beta).

        Raises:
            None.
        """
        previous_years = [month.year - 1 for month in eligible.index]
        lagged = betas.reindex(
            index=previous_years,
            columns=eligible.columns,
        )
        lagged.index = eligible.index
        return self.terciles(lagged, eligible)
