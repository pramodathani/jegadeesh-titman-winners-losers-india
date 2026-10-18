# Results

## Headline: 6-month ranking, 6-month holding, no skipped week

This strategy was fixed as the headline in the approved plan (commit 434bcff) before any result was seen. Holding months January 2007 to September 2026, 237 months. Costs use brahmagupta's 2026 NSE delivery rates with market impact of 0.3% a side for universe A (every share) and 0.1% for universe B (the liquid 500). The long-short portfolio is a paper portfolio: Indian investors cannot short cash shares overnight, and no borrowing cost is charged.

| Universe | Portfolio | Gross mean/month | Net mean/month | Newey-West t (net) | CAGR before costs | CAGR after costs | Excess over NIFTY 500 TRI a year | Alpha a month after risk-free (t) | Worst drawdown | Turnover a month |
|---|---|---|---|---|---|---|---|---|---|---|
| A | long-short | 1.49% | 1.19% | 2.7 | 15.2% | 12.2% | - | - | -62% | 0.72 |
| A | long-only winners | 2.17% | 2.04% | 3.3 | 23.2% | 21.8% | 10.5% | 0.78% (t 2.4) | -72% | 0.32 |
| B | long-short | 1.48% | 1.33% | 2.8 | 14.3% | 13.3% | - | - | -65% | 0.71 |
| B | long-only winners | 1.79% | 1.73% | 3.0 | 18.6% | 18.2% | 6.8% | 0.45% (t 1.8) | -73% | 0.31 |

The NIFTY 500 total return index compounded at 11.4% a year over the same months.


## What the Indian data says

1. **Momentum is strong in Indian shares.** All 64 long-short strategies earn a positive mean before and after costs. The 6/6 strategy with no skip earns 1.49% a month in universe A (ordinary t 3.6) and 1.48% in universe B (t 3.2), against the paper's 0.95% (t 3.07). Skipping a week raises returns, as in the paper.
2. **Costs take 20% of the long-short return in universe A and 10% in universe B, not all of it.** After brahmagupta's delivery costs the 6/6 spread is 1.19% (A) and 1.33% (B) a month, with Newey-West t of 2.7 and 2.8. Turnover is high, 0.71 of the book a month, and drawdowns are deep.
3. **The profit is not market risk.** The spread's beta is -0.38 (A) and -0.49 (B), negative as in the paper (-0.08), so alphas are larger than raw returns.
4. **The winners carry the signal, as in the paper.** Winners earn 1.79% a month in universe B (t 3.5) and losers 0.32% (t 0.4); the loser leg is not significantly different from zero, matching the paper, where the abnormal return comes from the buy side.
5. **No January effect, but a strong March.** The paper's January loss does not appear: January is 1.52% (A) and 2.98% (B). India's financial year ends in March, which averages 4.33% (A) and 3.33% (B), with July and October also strong and April and December negative. Without March the spread is still positive (see the robustness table).
6. **The effect was weak in 2007-2011** (ordinary t 0.9 in A and 0.8 in B, including the 2009 momentum crash) and stronger later (Table VI).
7. **No long-run reversal in the main sample.** The cumulative spread is 13.5% (A) and 13.0% (B) after 12 months and 14.4% and 22.4% after 36, where the paper loses about half. The 1997-2006 sample for universe A does reverse (Table VII below).
8. **Announcement returns follow the paper's shape:** winners beat losers around results in the first months after ranking and lose to them in months 8 to 20 (Table IX).
9. **A long-only investor could have held it.** Winners decile, universe B, 6/6: 18.2% a year after costs against 11.4% for the NIFTY 500 total return, with a beta of 1.13 and a worst drawdown of -73%. The alpha over the risk-free rate is 0.45% a month, about 5.4% a year, but its t-statistic is only 1.8 (months to December 2025). It was not a smooth lead: at each year end from 2008 to 2013 the winners portfolio was behind the index (relative value 0.78 at the end of 2013), and it reached 2.48 at the end of 2025. Almost all of the excess return came after 2013.


## Caveats

- **Shorting is not possible for most Indian investors.** The long-short numbers are for a paper portfolio and charge no borrowing cost. Only the long-only results are investable.
- **Costs are 2026 rates applied to the whole sample.** Securities transaction tax and brokerage were higher in 2007. Market impact (0.3% and 0.1% a side) is an assumption.
- **Delisted shares are in the data, but their last trade is the last return.** Losses after it are not charged; see the delisting stress.
- **Corporate actions are incomplete.** NSE's list is reliable only from 2005; some bonuses are missing (an unadjusted 1:2 bonus is a -33% day that the cleaning rule does not catch) and genuine one-day falls beyond -50% were set to zero. Renamed shares appear as one share ending and another starting. Rights issues, mergers and demergers are not adjusted.
- **Universe A includes penny stocks,** with monthly returns above 300% in the late 1990s. Universe B excludes them by construction.
- **Size is a proxy.** Before February 2024 there is no free market-capitalisation series, so size terciles use median daily traded value.
- **The risk-free rate stops in December 2025** and results announcements stop in March 2025, so alphas and Table IX use shorter samples.
- **The sample is 237 months,** against the paper's 300, and the strongest evidence is after 2011.
- **The skipped week is implemented as holding that starts five sessions after ranking,** which is what the paper describes; the plan wrote it the other way round, with the ranking ending five sessions earlier. The two are equivalent in what they avoid.


## How many variants were tried

Table I runs 64 strategies: 32 J/K combinations on each of 2 universes (16 with and 16 without the skipped week per universe). Each is scored long-short and long-only, so 128 series are scored. 64 of 64 long-short strategies have a positive mean before costs and 64 after costs. With 64 tests, a Bonferroni cutoff for a 5% two-sided level is |t| > 3.36; 20 of 64 pass on Newey-West t-statistics. The 64 strategies are highly correlated, so this cutoff is conservative. Tables II to IX use only the 6/6 strategy. The robustness checks add 6 variants for each of 2 universes and the delisting stress 4 treatments for each. No parameter was tuned on results.


## Table I: buy-minus-sell returns of the 32 strategies

Paper: NYSE and AMEX, 1965-1989 (page 70). India: NSE, 2007-2026. Cells give the mean monthly return before costs with its ordinary t-statistic, as the paper reports, and the paper's value after the bar. Second tables give the return after costs with the Newey-West t-statistic.

**Universe A, no skip**

Before costs | paper:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.01% (t 2.9) \| 0.32% | 1.13% (t 3.6) \| 0.58% | 0.98% (t 3.3) \| 0.61% | 0.97% (t 3.4) \| 0.69% |
| J=6 | 1.55% (t 3.6) \| 0.84% | 1.49% (t 3.6) \| 0.95% | 1.38% (t 3.5) \| 1.02% | 1.14% (t 3.0) \| 0.86% |
| J=9 | 1.69% (t 3.5) \| 1.09% | 1.67% (t 3.6) \| 1.21% | 1.39% (t 3.1) \| 1.05% | 1.19% (t 2.8) \| 0.82% |
| J=12 | 1.88% (t 3.7) \| 1.31% | 1.59% (t 3.1) \| 1.14% | 1.32% (t 2.7) \| 0.93% | 1.12% (t 2.5) \| 0.68% |

After costs, Newey-West t:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 0.49% (t 1.4) | 0.84% (t 2.5) | 0.77% (t 2.4) | 0.79% (t 2.5) |
| J=6 | 1.14% (t 2.4) | 1.19% (t 2.7) | 1.15% (t 2.6) | 0.95% (t 2.3) |
| J=9 | 1.33% (t 2.5) | 1.40% (t 2.7) | 1.16% (t 2.3) | 0.99% (t 2.1) |
| J=12 | 1.55% (t 2.8) | 1.34% (t 2.4) | 1.10% (t 2.1) | 0.92% (t 1.9) |

**Universe A, one week skipped**

Before costs | paper:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.30% (t 3.8) \| 0.73% | 1.31% (t 4.2) \| 0.78% | 1.13% (t 3.8) \| 0.74% | 1.06% (t 3.8) \| 0.77% |
| J=6 | 1.83% (t 4.2) \| 1.14% | 1.66% (t 4.0) \| 1.10% | 1.49% (t 3.8) \| 1.08% | 1.24% (t 3.3) \| 0.90% |
| J=9 | 1.91% (t 3.9) \| 1.35% | 1.81% (t 3.9) \| 1.30% | 1.51% (t 3.4) \| 1.09% | 1.30% (t 3.2) \| 0.85% |
| J=12 | 2.03% (t 4.0) \| 1.49% | 1.72% (t 3.5) \| 1.21% | 1.44% (t 3.1) \| 0.96% | 1.23% (t 2.9) \| 0.69% |

After costs, Newey-West t:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 0.78% (t 2.1) | 1.02% (t 3.0) | 0.92% (t 2.8) | 0.89% (t 2.9) |
| J=6 | 1.42% (t 2.9) | 1.37% (t 3.0) | 1.27% (t 2.9) | 1.05% (t 2.6) |
| J=9 | 1.55% (t 2.9) | 1.54% (t 3.0) | 1.28% (t 2.6) | 1.11% (t 2.5) |
| J=12 | 1.70% (t 3.1) | 1.47% (t 2.7) | 1.23% (t 2.5) | 1.04% (t 2.3) |

**Universe B, no skip**

Before costs | paper:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.59% (t 4.0) \| 0.32% | 1.33% (t 3.7) \| 0.58% | 1.12% (t 3.3) \| 0.61% | 1.00% (t 3.1) \| 0.69% |
| J=6 | 1.75% (t 3.6) \| 0.84% | 1.48% (t 3.2) \| 0.95% | 1.28% (t 2.9) \| 1.02% | 1.05% (t 2.5) \| 0.86% |
| J=9 | 1.79% (t 3.4) \| 1.09% | 1.53% (t 3.0) \| 1.21% | 1.26% (t 2.6) \| 1.05% | 1.10% (t 2.4) \| 0.82% |
| J=12 | 1.77% (t 3.1) \| 1.31% | 1.38% (t 2.6) \| 1.14% | 1.17% (t 2.4) \| 0.93% | 1.04% (t 2.3) \| 0.68% |

After costs, Newey-West t:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.32% (t 3.2) | 1.18% (t 3.3) | 1.01% (t 2.9) | 0.91% (t 2.7) |
| J=6 | 1.53% (t 3.1) | 1.33% (t 2.8) | 1.17% (t 2.5) | 0.96% (t 2.1) |
| J=9 | 1.60% (t 2.9) | 1.39% (t 2.5) | 1.14% (t 2.2) | 1.00% (t 2.1) |
| J=12 | 1.60% (t 2.7) | 1.25% (t 2.2) | 1.06% (t 2.0) | 0.95% (t 2.0) |

**Universe B, one week skipped**

Before costs | paper:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.68% (t 4.2) \| 0.73% | 1.41% (t 3.9) \| 0.78% | 1.20% (t 3.5) \| 0.74% | 1.02% (t 3.1) \| 0.77% |
| J=6 | 1.82% (t 3.7) \| 1.14% | 1.53% (t 3.3) \| 1.10% | 1.31% (t 3.0) \| 1.08% | 1.09% (t 2.6) \| 0.90% |
| J=9 | 1.84% (t 3.3) \| 1.35% | 1.55% (t 2.9) \| 1.30% | 1.28% (t 2.6) \| 1.09% | 1.13% (t 2.5) \| 0.85% |
| J=12 | 1.78% (t 3.1) \| 1.49% | 1.39% (t 2.5) \| 1.21% | 1.20% (t 2.4) \| 0.96% | 1.07% (t 2.4) \| 0.69% |

After costs, Newey-West t:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 1.42% (t 3.4) | 1.26% (t 3.4) | 1.08% (t 3.1) | 0.93% (t 2.7) |
| J=6 | 1.61% (t 3.1) | 1.38% (t 2.8) | 1.19% (t 2.5) | 0.99% (t 2.2) |
| J=9 | 1.65% (t 2.8) | 1.41% (t 2.5) | 1.17% (t 2.2) | 1.03% (t 2.2) |
| J=12 | 1.60% (t 2.7) | 1.25% (t 2.2) | 1.09% (t 2.1) | 0.97% (t 2.1) |


## Long-only winners, universe B, after costs

Compound annual return after costs, with the excess over the NIFTY 500 total return in brackets. Worst drawdowns are in `table_one.csv`.

No skip:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 18.4% (7.1%) | 16.7% (5.3%) | 15.3% (4.0%) | 14.5% (3.1%) |
| J=6 | 19.6% (8.3%) | 18.2% (6.8%) | 16.0% (4.6%) | 14.5% (3.1%) |
| J=9 | 19.9% (8.5%) | 17.2% (5.8%) | 15.1% (3.7%) | 14.3% (2.9%) |
| J=12 | 18.6% (7.2%) | 16.1% (4.7%) | 14.6% (3.2%) | 14.2% (2.8%) |

One week skipped:

|  | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| J=3 | 17.9% (6.5%) | 16.2% (4.8%) | 14.9% (3.5%) | 13.8% (2.4%) |
| J=6 | 19.0% (7.6%) | 17.5% (6.1%) | 15.3% (3.9%) | 14.0% (2.6%) |
| J=9 | 19.1% (7.7%) | 16.4% (5.1%) | 14.5% (3.2%) | 13.8% (2.5%) |
| J=12 | 17.5% (6.2%) | 15.5% (4.2%) | 14.2% (2.8%) | 13.7% (2.4%) |


## Table II: betas of the 6/6 deciles (page 73)

|  | P1 (losers) | P2 | P5 | P9 | P10 (winners) | P10-P1 |
|---|---|---|---|---|---|---|
| India A | 1.52 | 1.41 | 1.27 | 1.13 | 1.13 | -0.38 |
| India B | 1.62 | 1.50 | 1.25 | 1.10 | 1.13 | -0.49 |
| Paper | 1.36 | 1.19 | 1.09 | 1.17 | 1.28 | -0.08 |

Betas are against the NIFTY 500 total return. The paper also reports average market capitalisation; India has no free market-cap history before February 2024, so `table_two.csv` gives the median daily traded value in crore rupees instead.

## Table III: 6/6 spread by size and beta subsample (page 78)

|  | All | S1 small | S2 | S3 large | B1 low beta | B2 | B3 high beta |
|---|---|---|---|---|---|---|---|
| India A | 1.49% (t 3.6) | 1.17% (t 2.9) | 1.98% (t 4.5) | 1.53% (t 3.4) | 1.57% (t 3.6) | 1.64% (t 3.8) | 1.43% (t 3.5) |
| India B | 1.48% (t 3.2) | 1.87% (t 3.8) | 1.78% (t 3.8) | 0.65% (t 1.3) | 1.62% (t 3.7) | 1.46% (t 3.4) | 1.27% (t 2.6) |
| Paper | 0.95% | 0.99% | 1.26% | 0.75% | 0.62% | 0.79% | 1.08% |

Size subsamples are thirds of the median daily traded value, a proxy for size. Alphas against the NIFTY 500 total return excess of the risk-free rate (months to December 2025) are in `table_three.csv`.


## Tables IV and V: 6/6 spread by calendar month (pages 80-81)

| Month | India A | India B | Paper |
|---|---|---|---|
| Jan | 1.52% (t 1.2, 65% up) | 2.98% (t 1.9, 85% up) | -6.86% |
| Feb | 2.36% (t 3.0, 80% up) | 2.21% (t 2.8, 75% up) | 0.63% |
| Mar | 4.33% (t 4.8, 80% up) | 3.33% (t 2.6, 70% up) | 1.05% |
| Apr | -3.16% (t -1.6, 50% up) | -2.44% (t -1.4, 40% up) | 3.33% |
| May | 0.91% (t 0.4, 70% up) | 0.92% (t 0.3, 80% up) | 1.02% |
| Jun | 0.89% (t 0.5, 75% up) | -0.29% (t -0.2, 60% up) | 2.38% |
| Jul | 3.81% (t 6.3, 95% up) | 4.18% (t 6.2, 90% up) | 0.75% |
| Aug | 2.69% (t 2.3, 80% up) | 2.99% (t 2.2, 70% up) | 0.27% |
| Sep | 0.41% (t 0.5, 55% up) | 1.79% (t 1.8, 65% up) | 1.16% |
| Oct | 4.36% (t 3.7, 89% up) | 2.74% (t 1.8, 74% up) | 1.37% |
| Nov | 1.29% (t 1.0, 79% up) | 0.97% (t 0.8, 79% up) | 3.72% |
| Dec | -1.57% (t -1.2, 47% up) | -1.78% (t -1.2, 37% up) | 2.64% |
| Feb-Dec | 1.49% (t 3.4, 73% up) | 1.34% (t 2.8, 67% up) | 1.66% |

The paper finds a large negative January (-6.9%, positive in only 24% of years). India has no such January effect. March, July and October are the strongest months, March being the end of the Indian financial year, and April and December are negative. With 20 observations a month, single months are noisy.

## Table VI: 6/6 spread by subperiod (page 82)

|  | 2007-11 | 2012-16 | 2017-21 | 2022-Sep 26 |
|---|---|---|---|---|
| All, India A | 1.01% (t 0.9) | 1.73% (t 2.6) | 1.59% (t 1.8) | 1.63% (t 3.2) |
| All, India B | 0.98% (t 0.8) | 1.59% (t 2.0) | 2.00% (t 2.0) | 1.34% (t 2.5) |
| All except Mar, India A | 0.96% (t 0.8) | 1.33% (t 1.9) | 1.47% (t 1.5) | 1.14% (t 2.3) |
| All except Mar, India B | 1.00% (t 0.8) | 1.30% (t 1.6) | 1.83% (t 1.7) | 1.08% (t 2.0) |

Paper, all months, 1965-1989: 1965-69 1.23%, 1970-74 1.09%, 1975-79 -0.44%, 1980-84 1.27%, 1985-89 1.62%.


## Table VII: event time, cumulative 6/6 spread (page 84)

Cumulative winners-minus-losers return (sum of monthly averages) after 6, 12, 24 and 36 months with Newey-West t-statistics. Main sample: formation months December 2006 to September 2023.

|  | 6 months | 12 | 24 | 36 |
|---|---|---|---|---|
| India, 2007-2026, A | 9.0% (t 3.2) | 13.5% (t 2.7) | 13.9% (t 1.9) | 14.4% (t 1.3) |
| India, 2007-2026, B | 9.2% (t 3.2) | 13.0% (t 2.6) | 18.1% (t 2.4) | 22.4% (t 2.2) |
| India early sample, 1997-2006 (Table VIII stand-in), A | 3.5% (t 1.0) | 6.8% (t 1.4) | -2.3% (t -0.3) | -11.3% (t -0.9) |
| India early sample, 1997-2006 (Table VIII stand-in), B | 12.6% (t 3.8) | 20.7% (t 3.9) | 21.6% (t 2.8) | 13.7% (t 2.1) |
| Paper, 1965-1989 | 5.1% | 9.5% | 5.6% | 4.1% |

The paper finds that about half the first-year profit is lost in the next two years. In the main Indian sample the profit does not reverse; in the 1997-2006 sample it does for universe A. The early sample has less reliable corporate action data and many penny stocks, and stands in for the paper's pre-1965 back-test (Table VIII) only loosely.


## Section III: sources of the profits (pages 70-75)

|  | India A | India B | Paper |
|---|---|---|---|
| WRSS profit per dollar long per half-year | 0.0378 (t 1.48) | 0.0568 (t 2.92) | 0.0450 |
| serial covariance of half-year equal-weight index | 0.0063 | 0.0019 | -0.0028 |
| average serial covariance of residuals | -0.0078 | 0.0019 | 0.0012 |
| lead-lag theta, all | -0.9887 (t -1.63) | -0.8915 (t -1.39) | -2.2900 |


## Table IX: announcement-period returns (page 88)

Winners minus losers, 3-day return around quarterly results, by months since ranking. India: NSE results filings, August 2007 to March 2025 (NSE's results feed is nearly empty after that).

|  | Months 1-6 average | Months 8-20 average | Months 11-18 average |
|---|---|---|---|
| India A | 0.32% | -0.39% | -0.54% |
| India B | 0.67% | -0.36% | -0.31% |
| Paper | 0.70% | - | -0.70% |


## Robustness of the 6/6 long-short spread

| Variant | A gross (NW t) | A net | A net, double impact | B gross (NW t) | B net | B net, double impact |
|---|---|---|---|---|---|---|
| base | 1.49% (t 3.4) | 1.19% | 0.98% | 1.48% (t 3.1) | 1.33% | 1.26% |
| excluding 2009 | 1.81% (t 5.1) | 1.52% | 1.31% | 1.78% (t 4.6) | 1.63% | 1.56% |
| excluding March | 1.23% (t 2.6) | 0.93% | 0.71% | 1.31% (t 2.6) | 1.16% | 1.09% |
| excluding January | 1.49% (t 3.0) | 1.19% | 0.98% | 1.34% (t 2.5) | 1.19% | 1.12% |
| no big winners | 1.53% (t 3.5) | 1.24% | 1.02% | 1.47% (t 3.1) | 1.32% | 1.25% |
| winsorised at +100% | 1.53% (t 3.6) | 1.24% | 1.02% | 1.54% (t 3.3) | 1.39% | 1.32% |

**Delisting stress.** The bhavcopies give a share's last close but not what holders received on delisting, so nothing is charged after the last trade. As an extreme bound, a loss of 100% is charged in the month after the last return of every share that disappears for good (many such exits are mergers or symbol changes, so this overstates the harm). Mean monthly long-short return, before costs:

| Exit loss charged to | A | B |
|---|---|---|
| none | 1.49% (NW t 3.4) | 1.48% (NW t 3.1) |
| both legs | 1.65% (NW t 3.7) | 1.47% (NW t 3.1) |
| losers only | 2.02% (NW t 4.5) | 1.75% (NW t 3.7) |
| winners only | 1.13% (NW t 2.5) | 1.20% (NW t 2.5) |


## Cross-check with the IIMA momentum factor

Correlation of each monthly long-short series with the IIMA Indian WML factor (Agarwalla, Jacob and Varma), built independently from CMIE Prowess data, January 2007 to December 2025.

| Universe | Correlation, 6/6 no skip | Lowest over 32 strategies | Highest | Our 6/6 mean | IIMA mean |
|---|---|---|---|---|---|
| A | 0.76 | 0.53 | 0.78 | 1.46% | 1.03% |
| B | 0.83 | 0.56 | 0.85 | 1.46% | 1.03% |
