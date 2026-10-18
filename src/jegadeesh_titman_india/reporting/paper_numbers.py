"""Numbers printed in Jegadeesh and Titman (1993), with their pages."""

from typing import ClassVar


class PaperNumbers:
    """The paper's figures that the Indian tables are set beside.

    Attributes:
        TABLE_II_BETA: Table II (page 73), betas of the 6/6 deciles.
        TABLE_III_ALL_P10_P1: Table III Panel A (page 78), 6/6 spread.
        TABLE_IV: Table IV (page 80), 6/6 spread by calendar month, All.
        TABLE_VI: Table VI (page 82), 6/6 spread by subperiod, All months.
        TABLE_VII: Table VII (page 84), cumulative zero-cost return.
        TABLE_IX: Table IX (page 88), winners minus losers 3-day returns.
    """

    TABLE_II_BETA: ClassVar[dict[str, float]] = {
        '1': 1.36,
        '2': 1.19,
        '5': 1.09,
        '9': 1.17,
        '10': 1.28,
        'P10-P1': -0.08,
    }
    TABLE_III_ALL_P10_P1: ClassVar[dict[str, float]] = {
        'All': 0.0095,
        'S1': 0.0099,
        'S2': 0.0126,
        'S3': 0.0075,
        'B1': 0.0062,
        'B2': 0.0079,
        'B3': 0.0108,
    }
    TABLE_IV: ClassVar[dict[str, float]] = {
        'Jan': -0.0686,
        'Feb': 0.0063,
        'Mar': 0.0105,
        'Apr': 0.0333,
        'May': 0.0102,
        'Jun': 0.0238,
        'Jul': 0.0075,
        'Aug': 0.0027,
        'Sep': 0.0116,
        'Oct': 0.0137,
        'Nov': 0.0372,
        'Dec': 0.0264,
        'Feb-Dec': 0.0166,
    }
    TABLE_V_JAN: float = 0.24
    TABLE_VI: ClassVar[dict[str, float]] = {
        '1965-69': 0.0123,
        '1970-74': 0.0109,
        '1975-79': -0.0044,
        '1980-84': 0.0127,
        '1985-89': 0.0162,
    }
    TABLE_VII_CUMULATIVE: ClassVar[dict[int, float]] = {
        6: 0.0510,
        12: 0.0951,
        24: 0.0556,
        36: 0.0406,
    }
    TABLE_IX_FIRST_SIX_MONTHS: float = 0.007
    TABLE_IX_MONTHS_11_TO_18: float = -0.007
    SECTION_III: ClassVar[dict[str, float]] = {
        'WRSS profit per dollar long per half-year': 0.045,
        'serial covariance of half-year equal-weight index': -0.0028,
        'average serial covariance of residuals': 0.0012,
        'lead-lag theta, all': -2.29,
    }
