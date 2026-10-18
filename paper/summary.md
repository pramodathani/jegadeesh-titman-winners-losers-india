# Summary: Jegadeesh and Titman (1993)

Jegadeesh, N. and Titman, S. (1993), Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency, *The Journal of Finance* 48(1), 65-91, doi:10.1111/j.1540-6261.1993.tb04702.x. Page numbers below are the journal's printed pages (65-91); the PDF has a JSTOR cover page, so PDF page = journal page - 63.

## Hypothesis

Stocks that did well over the past 3 to 12 months keep doing better than stocks that did badly, over the next 3 to 12 months (p. 66-67). Relative strength ("momentum") strategies that buy past winners and sell past losers therefore earn significant returns. This runs against the contrarian evidence then in vogue, which was at very short horizons (1 week to 1 month: Jegadeesh 1990, Lehmann 1990) or very long ones (3 to 5 years: De Bondt and Thaler 1985). The authors ask whether the profits are compensation for systematic risk, a lead-lag reaction to common factors, or delayed reaction to firm-specific news (p. 67).

## Data

- CRSP daily returns file, July 1962 to December 1989, NYSE and AMEX stocks; monthly returns by compounding daily returns (p. 68-69, footnote 4).
- Main sample January 1965 to December 1989 (300 months); 1965 is the first full year because the 12/12 strategy needs 23 months of lagged data (footnote 4, p. 69).
- Back-test periods 1927-1940 and 1941-1964 (Section VII, p. 85).
- Every stock with returns over the past J months enters the ranking (p. 69). No price, size or liquidity filter is stated.
- Benchmarks: CRSP value-weighted and equally weighted indices; 1-month Treasury bill for the risk-free rate (p. 77).
- Earnings announcement dates from the 1990 COMPUSTAT quarterly file, 1980-1989, about 429.2 announcements per month (p. 87).

## Method

**Strategies (Section I, p. 68).** At the start of each month t, rank stocks on their past J-month return (J = 3, 6, 9, 12). Form ten equally weighted deciles. Buy the top decile (winners), sell the bottom decile (losers), and hold for K months (K = 3, 6, 9, 12): 16 strategies. A second set of 16 skips one week between the ranking period and the holding period, to avoid bid-ask bounce, price pressure and short-run reversal (p. 68). That makes 32 strategies.

The paper's wording swaps the labels on p. 68 ("the top decile portfolio is called the 'losers' decile"), but Table I's caption (p. 70) is clear: the lowest past-return decile is the *sell* portfolio and the highest is the *buy* portfolio. The code will follow the caption.

**Overlapping portfolios (p. 68).** In any month the strategy holds K cohorts, formed in months t, t-1, ..., t-K+1, each with weight 1/K. Each month it opens one cohort and closes the one from t-K, so 1/K of the book turns over. Returns are reported for portfolios rebalanced monthly to equal weights. Buy-and-hold portfolios gave very similar, slightly higher returns and are not shown (p. 68).

**Statistics.** Table I reports mean monthly returns with t-statistics in parentheses. The type of standard error is not stated for Table I. Newey-West (autocorrelation-consistent) errors are used for the cumulative event-time returns (footnote 16, p. 83) and in the regression of Section III.D (p. 75). The paper mentions a Bonferroni bound across the 32 tests (p. 69, footnote 5).

**Decomposition (Section III, p. 70-75).** With a one-factor model, the profit of a weighted relative strength strategy (WRSS) splits into three parts: cross-sectional dispersion in expected returns, factor serial covariance times beta dispersion, and serial covariance of idiosyncratic returns (eq. 3, p. 72). A lead-lag model (eq. 5-8, p. 74-75) is tested by regressing 6-month WRSS or decile-strategy profits on the lagged squared market return.

**Risk adjustment (eq. 9, p. 77).** Jensen's alpha from a market-model regression of excess portfolio returns on excess returns of the value-weighted index.

**Costs (p. 77).** Turnover of the 6/6 strategy is 84.8% every six months (buy side 86.6%, sell side 83.1%, footnote 12). With 0.5% one-way cost, the risk-adjusted return is 9.29% a year and remains significant.

## Results, table by table

### Table I (p. 70): returns of the 32 relative strength portfolios, 1965-1989

Mean monthly return of the buy-minus-sell portfolio (t-statistic). The full table, with the buy and sell legs, is in `paper_table_i.csv` (96 cells, checked for Buy - Sell = Buy-sell).

| J | Panel A: K=3 | K=6 | K=9 | K=12 | Panel B (skip 1 week): K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.0032 (1.10) | 0.0058 (2.29) | 0.0061 (2.69) | 0.0069 (3.53) | 0.0073 (2.61) | 0.0078 (3.16) | 0.0074 (3.36) | 0.0077 (4.00) |
| 6 | 0.0084 (2.44) | 0.0095 (3.07) | 0.0102 (3.76) | 0.0086 (3.36) | 0.0114 (3.37) | 0.0110 (3.61) | 0.0108 (4.01) | 0.0090 (3.54) |
| 9 | 0.0109 (3.03) | 0.0121 (3.78) | 0.0105 (3.47) | 0.0082 (2.89) | 0.0135 (3.85) | 0.0130 (4.09) | 0.0109 (3.67) | 0.0085 (3.04) |
| 12 | 0.0131 (3.74) | 0.0114 (3.40) | 0.0093 (2.95) | 0.0068 (2.25) | 0.0149 (4.28) | 0.0121 (3.65) | 0.0096 (3.09) | 0.0069 (2.31) |

- All 32 zero-cost returns are positive. All are significant except 3/3 without the skip (p. 69).
- The best is 12/3: 1.31% a month (Panel A) and 1.49% (Panel B, t = 4.28). Bonferroni p < 0.0006 over 32 tests (p. 69).
- J = 6 earns about 1% a month for every K. Skipping a week raises returns slightly.
- Buy legs are all significant (t 3.57 to 4.73). Sell legs mostly are not (t 0.93 to 2.16).

### Table II (p. 73): betas and size of the 6/6 deciles

| | P1 (losers) | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 (winners) | P10-P1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Beta (VW index) | 1.36 | 1.19 | 1.14 | 1.11 | 1.09 | 1.08 | 1.09 | 1.12 | 1.17 | 1.28 | -0.08 |
| Average market cap | 208.24 | 480.07 | 545.31 | 618.85 | 692.89 | 702.51 | 738.09 | 758.87 | 680.18 | 495.13 | |

The extreme deciles hold small, high-beta stocks; losers are smaller than winners. The WML beta is negative, so risk does not explain the profit. The paper does not give the units of market cap.

### Section III.C-D (p. 73-75): no table

- Serial covariance of 6-month equally weighted index returns: -0.0028. Average serial covariance of market-model residuals: +0.0012.
- The WRSS earns 4.5% per dollar long every six months (t = 2.99), with a correlation of 0.95 with the decile strategy (p. 71).
- Lead-lag regression, θ on lagged squared VW market return: -2.29 (t = -1.74). In the two halves: -2.55 (-2.65) and -1.83 (-2.52). For the WRSS: -1.77 (-3.56) (footnote 9). This is inconsistent with a lead-lag explanation.

### Table III (p. 78-79): 6/6 deciles within size and beta terciles

Panel A gives raw returns and Panel B gives Jensen alphas against the CRSP VW index. S1-S3 are size terciles and β1-β3 are Scholes-Williams beta terciles from the prior calendar year.

| P10-P1 | All | S1 | S2 | S3 | β1 | β2 | β3 |
|---|---|---|---|---|---|---|---|
| Panel A raw | 0.0095 (3.07) | 0.0099 (2.77) | 0.0126 (4.57) | 0.0075 (3.03) | 0.0062 (2.05) | 0.0079 (2.64) | 0.0108 (3.35) |
| Panel B alpha | 0.0100 (3.23) | 0.0106 (2.97) | 0.0129 (4.69) | 0.0076 (3.08) | 0.0063 (2.09) | 0.0083 (2.76) | 0.0111 (3.42) |

- The decile returns P1-P10 for "All" run from 0.0079 to 0.0174. The full decile panels are on p. 78-79; the extracted text shows a minus sign on S3/P4, but the page image shows +0.0105.
- Winner alphas are significant; loser alphas are not, against the VW index (p. 77).
- Against the EW index, the WML alpha is 0.0115 (t = 3.84) (p. 77).

### Table IV (p. 80): 6/6 WML by calendar month (All, S1, S2, S3)

- January: -0.0686 (t = -3.52) for All, -0.0797 for S1, -0.0347 for S2, -0.0161 (t = -1.28) for S3.
- February-December: 0.0166 (6.67) for All. April 0.0333 (7.39), November 0.0372 (5.31), December 0.0264 (2.61).
- F-tests of equal returns across all months reject for All, S1 and S2. Within February-December they reject for All (p = 0.03) and S2.

### Table V (p. 81): share of months with positive 6/6 WML

All: 0.67 overall, 0.71 in February-December, 0.24 in January, 0.96 in April (24 of 25 years).

### Table VI (p. 82): 6/6 WML by 5-year subperiod

All months: 1965-69 0.0123, 1970-74 0.0109, 1975-79 -0.0044, 1980-84 0.0127, 1985-89 0.0162. The 1975-79 loss comes from January returns of small firms. Every subperiod and size group is positive in February-December.

### Table VII (p. 84): 6-month-ranked WML in event time, months 1-36

- Month 1: -0.0025.
- Months 2-12 are positive, and the cumulative return peaks at 0.0951 (t = 3.67) in month 12.
- Months 13-30 are negative, and the cumulative return falls to 0.0406 (t = 0.67) by month 36.
- The beta against the VW index rises from -0.20 to 0.02 over event time (p. 84).

### Table VIII (p. 86-87): event-time back-tests

- Panel A, 1927-1940: month 1 is -0.0495, and the cumulative return reaches -0.4081 by month 36. There were momentum crashes such as July-August 1932 (-40% and -68%) (p. 85).
- Panel B, 1941-1964: the cumulative return peaks at 0.0592 in month 11 and is about 0 by month 24.

### Table IX (p. 88): 3-day earnings-announcement returns, winners minus losers, 1980-1989

- Months 1-6 are positive, 0.0055 to 0.0090, all significant.
- Months 8-20 are negative, with months 11-18 averaging about -0.7%.
- Announcement returns explain about 25% of the 6/6 profit in the first six months (p. 88).

## Conclusions (p. 89-90)

- Momentum earns about 1% a month; the 6/6 strategy compounds to 12.01% a year.
- It is not explained by systematic risk or by a lead-lag reaction to common factors. It is consistent with delayed reaction to firm-specific news.
- About half the first-year excess return reverses over the next two years, so simple stories of underreaction or overreaction are too simple. Positive-feedback traders, or underreaction in the short term and overreaction in the long term, are both possible.

## What can be reproduced for India

| Paper item | Reproducible for NSE? | Notes for the Adapt-to-India stage |
|---|---|---|
| Table I, 32 J/K strategies | Yes | Bhavcopies 1995-2026. "Skip a week" maps to skipping 5 trading days. Short selling is not practical overnight in cash, so long-short is a paper portfolio. |
| Table II, betas and size | Yes | Market cap needs shares outstanding, which bhavcopies may lack; use traded value or an index constituent proxy if not. To settle at Adapt to India. |
| Section III WRSS, serial covariances, lead-lag regression | Yes | Needs only returns and an index. |
| Table III, size and beta terciles, alphas | Yes, with a size proxy | Needs an Indian risk-free rate (91-day T-bill) and a market index (NIFTY 500 TRI). |
| Tables IV-V, calendar months | Yes | January has no tax-loss reason in India; March (financial year end) is the natural Indian analogue. |
| Table VI, subperiods | Yes | Five-year blocks from about 1997 onward. |
| Table VII, event time 36 months | Yes | |
| Table VIII, pre-1965 back-test | Not as such | No pre-1995 NSE data. A split-sample check of the Indian period stands in for it. |
| Table IX, earnings announcements | Perhaps | Needs NSE results dates; to settle at Adapt to India. |
| Costs (0.5% one-way, 84.8% turnover) | Yes, improved | Use brahmagupta's Indian delivery costs. Add long-only versions against the NIFTY 500. |
