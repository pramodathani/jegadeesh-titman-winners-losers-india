# Data

Everything here is git-ignored except this file. Raw exchange data is never published; only derived results are. Fetched on 2026-10-18 (India time) with `python -m jegadeesh_titman_india.data.downloads data 2026-10-16`, which skips files already on disk. Data runs to the 2026-10-16 session.

## From the earlier study's data folder (read-only, linked in `external/`)

Persona rule: only the downloaded data of `/home/pramod/Projects/research/jstor/jegadeesh_and_titman/data/` is used; its code, results and processed Parquet store are not.

| Link | Points to | Contents | Counts |
|---|---|---|---|
| `external/earlier_bhavcopy_raw` | `bhavcopy/raw` | Daily share bhavcopy zips, `{year}/{date}.csv.zip`, old CSV format to 2024-07-05 and UDiFF from 2024-07-08, plus `not_available.txt` (430 dates NSE had no file for) | 7,857 files, 1995-01-02 to 2026-10-06; 242 to 252 sessions a year |
| `external/earlier_corporate_actions` | `bhavcopy/corporate_actions` | NSE corporate actions JSON per year (the API behind NSE's corporate actions page); complete only from 2005 | 32 files, 1995 to 2026 |
| `external/earlier_index_daily` | `indices/nse_daily` | NSE daily index files (`ind_close_all`), all indices incl. dividend yield | 3,505 files, 2012-07-02 to 2026-10-06 |

Shares with series EQ, BE or BZ on the year's last session: 944 (1995), 874 (2005), 1,191 (2007), 1,689 (2019), 2,942 (2026-10-06).

## Downloaded for this study (`nse/`)

| Path | Source | Contents | Counts |
|---|---|---|---|
| `nse/bhavcopy_raw/2026/` | `https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{YYYYMMDD}_F_0000.csv.zip` | UDiFF bhavcopies for the sessions after the earlier files end | 8 files, 2026-10-07 to 2026-10-16; 2,949 EQ/BE/BZ shares on the last day |
| `nse/corporate_actions/2026.json` | `https://www.nseindia.com/api/corporates-corporateActions` | 2026 refreshed to 2026-10-16; replaces the earlier study's 2026 file | 1,849 actions, latest ex-date 2026-10-16 |
| `nse/nifty500_tri.json` | `POST https://www.niftyindices.com/BackPage/getTotalReturnIndexString` | NIFTY 500 total return index, daily; `NTR_Value` is filled only from 2015 | 7,879 rows, 1995-01-01 to 2026-10-16, no duplicate dates |
| `nse/iima/2025-12_FourFactors_and_Market_Returns_Monthly_SurvivorshipBiasAdjusted.csv` | `https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/` | Columns Date, SMB, HML, WML, MF, RF; monthly returns in percent; RF from RBI 91-day T-bill auctions; WML is used only as an outside cross-check | 387 months, 1993-10 to 2025-12; 1993-10 has no RF |
| `nse/market_cap/PR{DDMMYY}.zip` | `https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/` | Last session of each month; each holds `MCAP{date}.csv` with issue size and market cap | 33 files, 2024-02 to 2026-10; used only to validate the traded-value size proxy |
| `nse/results/{year}.json` | `https://www.nseindia.com/api/corporates-financial-results` | Quarterly results filings with broadcast and filing times; standalone and consolidated are separate rows | 2007: 4,271 rows; 2012: 7,768; 2020: 11,374; 2024: 14,329 |
| `nse_download.log` | | Output of the download job | |

## From UBI through tradingmachine (`ubi/`)

| Path | Contents | Counts |
|---|---|---|
| `ubi/instruments_nse_equities.parquet` | UBI's NSE equities master | 3,454 instruments |
| `ubi/daily_prices_nse_equities.parquet` | Daily candles, adjusted for splits and bonuses, not dividends (`price_factor` column) | 2,943,119 candles, 2,605 instruments, 2019-12-03 to 2026-10-16; 827 of 3,432 listed instruments have no candles |

Used only to cross-check this study's adjusted prices from December 2019. UBI cannot supply the history before that, delisted shares or dividends (gaps 1, 2, 7).

## Catches

- **Results dates stop in 2025.** The NSE API returns 3,865 rows for Q1 2025 but only 28, 8 and 59 for the next three quarters. Table IX can use filings from Aug 2007 to Mar 2025 only. Feb to Jul 2007 rows lack a broadcast time, so the filing time is used there.
- **No 2026 risk-free rate.** The IIMA file ends in December 2025 and no scriptable RBI or FRED series was reachable. Risk-adjusted numbers use RF through December 2025; returns and costs run to September 2026.
- **IIMA releases are recalculated.** Three times a year all values may change, so the release prefix `2025-12` stays in the file name.
- **Market cap before February 2024 is not available** from a free scriptable source; size is a traded-value proxy.
- **Delisted shares are in the bhavcopies.** Every share that traded appears while it traded, so there is no survivorship bias in prices; the corporate-action list is complete only from 2005.
- **Raw files are unadjusted;** NSE does not adjust PREVCLOSE either. The Build stage applies the corporate actions.
- **No bhavcopy for 430 listed dates** in the earlier study's `not_available.txt` (holidays and some missing archive days); the Build stage checks them against the index and UBI calendars.
