# Plan: Jegadeesh and Titman (1993) on NSE shares

Status: proposed for approval at the Adapt-to-India gate, 2026-10-18.

## 1. What the study will do

- **Rebuild the paper on NSE shares.** All 32 J/K strategies of Table I, the decomposition tests of Section III, and Tables II-VII and IX, on NSE shares with Indian data.
- **Stand-in for Table VIII.** A back-test on an earlier, less clean sample takes its place.
- **Indian versions an investor could hold.** Long-only portfolios in a liquid universe, after Indian costs, against the NIFTY 500 total return.

## 2. What changes for India, and why

| Item | Paper (US) | India version | Why |
|---|---|---|---|
| Market and universe | NYSE and AMEX, every stock with J months of returns (p. 69) | **A. Paper universe:** every NSE share in series EQ, BE or BZ with J months of returns and a close in the last 5 trading days before formation. **B. Liquid 500:** the 500 shares with the highest median daily traded value over the previous 12 months, with trades on at least 80% of those days | A is the faithful copy. B is what an investor can trade; NSE's long tail is illiquid and often in trade-for-trade series |
| Delisted shares | CRSP includes them | Included: bhavcopies list every share that ever traded. A delisted share earns its last traded return, then its weight goes to the rest of its cohort | Avoids survivorship bias. UBI cannot do this (gap 2) |
| Dates | 1965-1989 holding periods; 1927-1964 back-test | **Main sample:** holding months Jan 2007 to Sep 2026 (237 months), the same for all 32 strategies. **Early sample:** Jan 1997 to Dec 2006 as the Table VIII stand-in | NSE's corporate-action list is complete only from 2005 (nse-market-data skill). The 12/12 strategy needs 23 months of history before a full year, like the paper's footnote 4 |
| Returns | CRSP daily returns, compounded to monthly | Daily total returns from bhavcopy closes, adjusted for splits, bonuses and dividends from NSE's corporate-action list, compounded to monthly | Bhavcopy prices are unadjusted |
| Skip a week (Panel B) | 1 week between ranking and holding | The ranking window ends 5 trading days before the formation date; holding starts at the formation date | Same idea on Indian trading days |
| Weights | Equal weights, rebalanced monthly, K overlapping cohorts (p. 68) | The same, with brahmagupta's `OverlappingCohorts` | Faithful |
| Trading hours and settlement | NYSE | Monthly signals on closes, trades at the next close, T+1 delivery. Settlement does not affect monthly returns | Recorded for the hand-off |
| Short selling | Assumed free | The long-short (buy-minus-sell) portfolio is a **paper portfolio**. Overnight short sales of cash shares are not allowed for ordinary investors; securities lending is thin, and stock futures cover only about 200 F&O shares. Long-only versions are the investable result | The Indian market's rules |
| Costs | 0.5% one way, on the 6/6 strategy only (p. 77) | brahmagupta's Indian delivery costs on every strategy (brokerage, STT 0.1% each side, stamp duty, exchange and SEBI charges, GST), with impact 0.003 a side for universe A and 0.001 for B. Every result is shown before and after costs. The short leg of the paper portfolio is charged the same delivery costs, as an approximation | House rule |
| Market index for betas and alphas | CRSP value-weighted and equally weighted indices | NIFTY 500 total-return index from niftyindices.com (from 1 Jan 1995) as the value-weighted market; an equally weighted index of universe A built from our own returns | The closest Indian match. Using the total-return index avoids gap 12 (price-only indices) |
| Risk-free rate | 1-month Treasury bill | The 91-day T-bill return from the IIMA data library (RF column, 1995-01 to 2025-12, from RBI auctions). For 2026 months: RBI's 91-day auction cut-off yields, or failing that the last value carried forward, flagged | There is no Indian 1-month bill series; 91-day is the standard. Gap 15 |
| Size (Tables II-IV, VI) | Market capitalisation | **Proxy:** median daily traded value over the past 12 months. Checked against true market cap from NSE's daily MCAP files (Feb 2024 onward) by rank correlation | NSE has no free shares-outstanding history before Feb 2024 (gap 10) |
| Beta terciles (Table III) | Scholes-Williams betas from the prior calendar year's daily returns | The same, against the NIFTY 500 total return | Faithful |
| Calendar months (Tables IV-V) | The January effect | All 12 months reported. The Indian analogue of January's tax and window-dressing effect is March, the financial-year end | India's tax year ends in March |
| Earnings dates (Table IX) | COMPUSTAT dates, 1980-1989, days -2 to 0 | NSE results filings (`corporates-financial-results` API) from Aug 2007, using the earliest broadcast time per symbol and quarter. Day 0 is the first session that could react; filings after 15:30 move to the next day | The only free source with timestamps. Feb-Jul 2007 rows use the filing date |
| Statistics | t-statistics, NW for cumulative returns | Newey-West t-statistics for every mean, with the number of months and the worst drawdown. Plain OLS t is also shown in Table I so it can be compared with the paper | House rule |

## 3. Data, and where it comes from

UBI comes first by house rule. It cannot give this study's history, delisted shares or dividends (gaps 1, 2 and 7). So UBI is used only to **cross-check** our split- and bonus-adjusted prices for Dec 2019 onward, through `export_prices`, keeping gap 24 (the Feb-Mar 2022 hole) in mind.

Files read **read-only** from the earlier study, `/home/pramod/Projects/research/jstor/jegadeesh_and_titman/data/`, as the persona allows. I will not read that study's code, tests, results, README or site, so the parsing and adjustment code here is written fresh. The nse-market-data skill suggests copying its bhavcopy code; that is set aside for the sake of the comparison.

| File | Use |
|---|---|
| `bhavcopy/raw/{year}/*.csv.zip` (7,857 files, 1995-01-02 to 2026-10-06) and `bhavcopy/raw/not_available.txt` | Daily closes, previous closes and traded values. **Raw zips only**; the derived `bhavcopy/store/*.parquet` is that study's processed output and is not used |
| `bhavcopy/corporate_actions/{1995..2026}.json` | Splits, bonuses and dividends |
| `indices/nse_daily/*.csv` (2012-07-02 to 2026-10-06) | NIFTY 500 dividend yield, as a check on the total-return index only |

New downloads, into this study's git-ignored `data/`, resumable, with sources in `data/README.md`:

1. Bhavcopies from 2026-10-07 to the latest session (UDiFF format), and the 2026 corporate actions refreshed.
2. NIFTY 500 total-return index, daily from 1995: `POST https://www.niftyindices.com/BackPage/getTotalReturnIndexString`, one request.
3. The IIMA four-factor monthly file (`2025-12_FourFactors_and_Market_Returns_Monthly_SurvivorshipBiasAdjusted.csv`): the RF column, plus WML as an outside cross-check of our momentum series.
4. RBI 91-day T-bill auction yields for 2026 (manual or scripted, whichever works).
5. NSE MCAP files inside `PR{DDMMYY}.zip`, one per month-end from Feb 2024, to validate the size proxy.
6. NSE results filings 2007-2026 from `corporates-financial-results`, one request per year, for Table IX.

**Cleaning rules**, fixed in advance:
- Keep EQ, BE and BZ, preferring EQ when a share appears in more than one series.
- Set one-day returns below -50% or above +100% to zero when no corporate action explains them, and log each one.
- Check the adjustment on known events; examples are named in the tests.

## 4. Tables to reproduce

| Paper | India output | Notes |
|---|---|---|
| Table I (32 strategies, buy, sell, buy-sell) | Yes, for universes A and B, before and after costs | Headline |
| Section III: WRSS, serial covariances, lead-lag regression | Yes | |
| Table II (betas and size of 6/6 deciles) | Yes | Size is the traded-value proxy; market cap from 2024 shown alongside |
| Table III (size and beta terciles, raw and alpha) | Yes | |
| Tables IV-V (calendar months) | Yes | March focus |
| Table VI (5-year subperiods) | 2007-11, 2012-16, 2017-21, 2022-Sep 2026 | |
| Table VII (event time, 36 months) | Yes | |
| Table VIII (pre-1965 back-test) | Stand-in: event time on 1997-2006 | Less clean corporate actions; flagged |
| Table IX (earnings announcement returns) | Yes, Aug 2007 onward | |
| New: long-only | Winners decile of each J/K in universe B, equal weight, after costs, against the NIFTY 500 TRI | **The headline long-only result is fixed in advance as 6/6 without the skip**, the paper's own focus, so that it is not the best of 32 |
| New: cross-check | Our 12-month WML against IIMA's WML (correlation) | |

**Variant count.** I will report 32 strategies × 2 universes for the long-short, plus 32 for the long-only: 96 in all. The paper's Bonferroni argument (p. 69) is repeated across all 96, and the best one is reported with that caution.

## 5. Tests, all offline on small made-up data

1. **Parsing:** both bhavcopy formats (old CSV and UDiFF) parse to the same columns, and series priority works.
2. **Corporate actions:** a 1:1 bonus, a 10:1 split and a dividend give the right adjusted return on the ex-date.
3. **Extreme returns:** they are zeroed and logged.
4. **Monthly returns:** they compound daily returns, and a delisting mid-month earns its partial return.
5. **Ranking:** a J-month ranking uses only data before formation, with and without the 5-day skip, so there is no look-ahead.
6. **Deciles:** they split correctly with ties and small universes.
7. **Overlapping cohorts:** they give the hand-computed J/K portfolio return.
8. **Statistics:** Newey-West t, Scholes-Williams beta and the WRSS decomposition match hand-computed values.
9. **Event-time returns and the Table IX windows:** these follow the after-15:30 rule.
10. **Liquid-500 selection:** it uses only past data.

## 6. Where India cannot match the paper

- **No Indian history before 1995,** so there is no 60-year back-test. The early sample, 1997-2006, rests on corporate actions that may be incomplete.
- **Size is a traded-value proxy before 2024.** Size terciles will mix size with liquidity.
- **The long-short portfolio cannot be held as such in India.** Its after-cost numbers are an upper bound.
- **The sample is short.** About 20 years and 237 months, against the paper's 25 years and 300 months, so t-statistics will be smaller for the same effect.
- **The universe is very different.** Indian small caps are far less liquid than NYSE and AMEX stocks were. Universe A's returns may be inflated by stale prices and trade-for-trade shares, which is why universe B is there.
- **The risk-free rate is the 91-day T-bill, not 1-month,** with a small gap in 2026.
- **The NSE market's makeup has changed a great deal over 2007-2026,** which is a regime the paper never faced.
