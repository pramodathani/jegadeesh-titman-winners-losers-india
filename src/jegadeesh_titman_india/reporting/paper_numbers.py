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
    TABLE_II_BETA_ALL: ClassVar[list[float]] = [
        1.36,
        1.19,
        1.14,
        1.11,
        1.09,
        1.08,
        1.09,
        1.12,
        1.17,
        1.28,
    ]
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
    TABLE_VII_CUMULATIVE_ALL: ClassVar[list[float]] = [
        -0.0025,
        0.0099,
        0.0216,
        0.0326,
        0.0419,
        0.0510,
        0.0644,
        0.0759,
        0.0844,
        0.0892,
        0.0938,
        0.0951,
        0.0915,
        0.0876,
        0.0842,
        0.0804,
        0.0757,
        0.0701,
        0.0675,
        0.0642,
        0.0611,
        0.0577,
        0.0566,
        0.0556,
        0.0521,
        0.0492,
        0.0467,
        0.0435,
        0.0403,
        0.0373,
        0.0372,
        0.0380,
        0.0394,
        0.0402,
        0.0412,
        0.0406,
    ]
    TABLE_IX_ALL: ClassVar[list[float]] = [
        0.0055,
        0.0082,
        0.0082,
        0.0090,
        0.0059,
        0.0058,
        0.0013,
        0.0000,
        -0.0020,
        -0.0031,
        -0.0039,
        -0.0053,
        -0.0055,
        -0.0080,
        -0.0071,
        -0.0097,
        -0.0062,
        -0.0060,
        -0.0031,
        -0.0017,
        0.0006,
        -0.0005,
        -0.0001,
        0.0012,
        -0.0002,
        -0.0021,
        -0.0032,
        -0.0028,
        -0.0015,
        -0.0021,
        -0.0027,
        -0.0021,
        -0.0020,
        -0.0017,
        -0.0022,
        -0.0059,
    ]
