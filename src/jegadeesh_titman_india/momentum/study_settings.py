"""The fixed choices of the study, set out in the approved plan."""

from typing import ClassVar

import pandas as pd


class StudySettings:
    """Sample periods, strategy grid and cost assumptions.

    Attributes:
        MAIN_FIRST: The first holding month of the main sample.
        MAIN_LAST: The last holding month of the main sample.
        EARLY_FIRST: The first holding month of the early sample.
        EARLY_LAST: The last holding month of the early sample.
        RANKING_MONTHS: The values of J.
        HOLDING_MONTHS: The values of K.
        IMPACT_COST: Market impact per side for each universe.
        HEADLINE_RANKING: J of the headline long-only strategy.
        HEADLINE_HOLDING: K of the headline long-only strategy.
    """

    MAIN_FIRST: pd.Period = pd.Period('2007-01', freq='M')
    MAIN_LAST: pd.Period = pd.Period('2026-09', freq='M')
    EARLY_FIRST: pd.Period = pd.Period('1997-01', freq='M')
    EARLY_LAST: pd.Period = pd.Period('2006-12', freq='M')
    RANKING_MONTHS: tuple[int, ...] = (3, 6, 9, 12)
    HOLDING_MONTHS: tuple[int, ...] = (3, 6, 9, 12)
    IMPACT_COST: ClassVar[dict[str, float]] = {
        'A': 0.003,
        'B': 0.001,
    }
    HEADLINE_RANKING: int = 6
    HEADLINE_HOLDING: int = 6
