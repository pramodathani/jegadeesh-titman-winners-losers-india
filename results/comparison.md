# Comparison with the earlier study

This study (jt-pilot, made by a research-agent analyst) is set beside the earlier study of the same paper made with Claude Code (`jegadeesh_and_titman/results/bhavcopy_from_2005`). I read the earlier study's result tables and its README only after my own results were written and committed (commit 9e8bd55); I did not read its code or tests, and I changed nothing in my results afterwards. Both studies use the same 237 holding months, January 2007 to September 2026, the same NSE bhavcopy files and corporate actions, and two universes: every share (my A, their all_shares) and the 500 most traded (my B, their most_traded_500). Differences are mine minus theirs. The earlier study's numbers come from its own CSV files, read by `scripts/compare_with_earlier_study.py`.

## Table I: monthly mean of buy minus sell, before costs

| Universe | Panel | My average of 16 | Their average | Mean difference | Largest cell difference | Correlation of the 16 cells | Positive cells (mine and theirs) |
|---|---|---|---|---|---|---|---|
| A vs all_shares | no skip | 1.34% | 1.33% | 0.02% | 0.07% | 0.998 | 16/16 and 16/16 |
| A vs all_shares | skip | 1.50% | 1.36% | 0.14% | 0.20% | 0.995 | 16/16 and 16/16 |
| B vs most_traded_500 | no skip | 1.35% | 1.31% | 0.05% | 0.10% | 0.988 | 16/16 and 16/16 |
| B vs most_traded_500 | skip | 1.39% | 1.25% | 0.14% | 0.22% | 0.982 | 16/16 and 16/16 |

The 6/6 strategy without a skip, both legs:

| Universe | Leg | Mine | Theirs | Difference |
|---|---|---|---|---|
| A | buy | 2.17% | 2.08% | 0.09% |
| A | sell | 0.68% | 0.60% | 0.08% |
| A | buy_minus_sell | 1.49% | 1.48% | 0.01% |
| B | buy | 1.79% | 1.70% | 0.10% |
| B | sell | 0.32% | 0.32% | 0.00% |
| B | buy_minus_sell | 1.48% | 1.38% | 0.10% |


## Long-only winners in the liquid 500, after costs

|  | Mine | Theirs |
|---|---|---|
| Average compound annual return of the 32 portfolios | 16.1% | 15.2% |
| Correlation across the 32 portfolios | 0.986 |  |
| Highest compound annual return | 19.9% (J9/K3, no skip) | 18.9% (J9/K3, no skip) |
| 6/6 without skip, compound annual return | 18.2% | 16.6% |
| 6/6 without skip, worst drawdown | -73% | -73% |
| Benchmark compound annual return | 11.4% (NIFTY 500 total return index) | 11.5% (price index plus dividend yield) |
| Mean difference mine minus theirs, 32 portfolios | 0.92% |  |


## Calendar months, 6/6 spread (my Table IV, their table 4)


Universe A against all_shares; largest monthly difference 0.57%:

| Month | Mine | Theirs |
|---|---|---|
| Jan | 1.52% | 1.70% |
| Feb | 2.36% | 2.32% |
| Mar | 4.33% | 4.54% |
| Apr | -3.16% | -2.78% |
| May | 0.91% | 0.34% |
| Jun | 0.89% | 0.63% |
| Jul | 3.81% | 3.74% |
| Aug | 2.69% | 2.43% |
| Sep | 0.41% | 0.81% |
| Oct | 4.36% | 4.20% |
| Nov | 1.29% | 1.72% |
| Dec | -1.57% | -1.13% |

Universe B against most_traded_500; largest monthly difference 0.94%:

| Month | Mine | Theirs |
|---|---|---|
| Jan | 2.98% | 2.98% |
| Feb | 2.21% | 1.82% |
| Mar | 3.33% | 2.81% |
| Apr | -2.44% | -1.57% |
| May | 0.92% | -0.01% |
| Jun | -0.29% | 0.01% |
| Jul | 4.18% | 4.10% |
| Aug | 2.99% | 2.51% |
| Sep | 1.79% | 1.76% |
| Oct | 2.74% | 2.77% |
| Nov | 0.97% | 1.04% |
| Dec | -1.78% | -1.30% |


## Event time, cumulative spread (my Table VII, their table 7)

| Universe | Event month | Mine | Theirs |
|---|---|---|---|
| A vs all_shares | 6 | 9.0% | 9.2% |
| A vs all_shares | 12 | 13.5% | 13.8% |
| A vs all_shares | 24 | 13.9% | 12.7% |
| A vs all_shares | 36 | 14.4% | 12.0% |
| B vs most_traded_500 | 6 | 9.2% | 8.6% |
| B vs most_traded_500 | 12 | 13.0% | 12.5% |
| B vs most_traded_500 | 24 | 18.1% | 16.3% |
| B vs most_traded_500 | 36 | 22.4% | 18.4% |

Their formation months start in 2005 and mine in December 2006, which accounts for part of any gap.


## Decile betas against the NIFTY 500 (my Table II, their table 2)

| Universe | Portfolio | Mine | Theirs |
|---|---|---|---|
| A vs all_shares | P1 | 1.52 | 1.47 |
| A vs all_shares | P10 | 1.13 | 1.11 |
| A vs all_shares | P10-P1 | -0.38 | -0.36 |
| B vs most_traded_500 | P1 | 1.62 | 1.59 |
| B vs most_traded_500 | P10 | 1.13 | 1.13 |
| B vs most_traded_500 | P10-P1 | -0.49 | -0.46 |


## What differs between the studies

Taken from the earlier study's README and result files, and from my own plan:

- **Data start.** Theirs starts on 2005-01-03; mine uses 1995 bhavcopies, so my ranking inputs for early 2007 have the same depth but my early sample (1997-2006) exists and theirs does not.
- **Corporate actions.** They match each split or bonus to the trading day near its listed ex-date whose price drop fits the ratio and apply it only if it brings that day's return closer to zero. I apply each action on the first trading day on or after its listed ex-date. Their README reports 709 returns zeroed; mine zero 863 (1995-2026).
- **Funds.** I remove 521 ETF, fund and entitlement symbols by ISIN or name; their README does not mention removing funds.
- **Liquid universe.** Theirs ranks the previous six months of traded value; mine uses the previous 250 sessions with a minimum 80% trading share. Both keep 500 shares.
- **Benchmark.** Theirs is the NIFTY 500 price index plus a twelfth of the month's dividend yield (a later-year average yield before July 2012); mine is NSE's NIFTY 500 total return index, found on niftyindices.com from 1995.
- **Costs.** Both use brahmagupta-style Indian delivery costs with impact of 0.1% (liquid) and 0.3% (all); theirs also reports a fixed depository charge note.
- **Risk-free rate.** They use none; mine uses the IIMA 91-day bill series to December 2025.
- **Paper tables.** I add Table IX (announcement returns), Section III, Table VIII's stand-in, size and beta subsamples by terciles, a delisting stress and robustness checks. They do not replicate Table IX and use liquidity terciles only.
- **Plain versus Newey-West t.** Their t-statistics in Table I are ordinary ones, as the paper's appear to be; mine show both.
