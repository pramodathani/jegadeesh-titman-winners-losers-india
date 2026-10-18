"""Writes results/summary.md from the results tables."""

import pathlib

import pandas as pd
from scipy import stats

from jegadeesh_titman_india.reporting.markdown_table import MarkdownTable
from jegadeesh_titman_india.reporting.paper_numbers import PaperNumbers


class SummaryWriter:
    """Builds the results summary, each table set beside the paper's.

    Attributes:
        results: The folder with the results tables.
        paper: The folder with the paper's transcribed Table I.
        markdown: The table formatter.
    """

    def __init__(
        self,
        results: pathlib.Path,
        paper: pathlib.Path,
    ) -> None:
        """Creates the writer.

        Args:
            results: The results folder.
            paper: The paper folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.results = results
        self.paper = paper
        self.markdown = MarkdownTable()

    def read(self, name: str) -> pd.DataFrame:
        """Reads one results table.

        Args:
            name: The file name without the extension.

        Returns:
            The table.

        Raises:
            None.
        """
        return pd.read_csv(self.results / f'{name}.csv')

    def write(self) -> None:
        """Writes results/summary.md.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        parts = [
            self.headline(),
            self.findings(),
            self.caveats(),
            self.variants(),
            self.table_one(),
            self.long_only_grid(),
            self.tables_two_three(),
            self.tables_four_to_six(),
            self.tables_seven_eight(),
            self.section_three(),
            self.table_nine(),
            self.robustness(),
            self.cross_check(),
        ]
        text = '\n'.join(parts)
        (self.results / 'summary.md').write_text(text)

    def headline(self) -> str:
        """Writes the headline section.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        table = self.read('headline_strategies')
        impact = {'A': 0.003, 'B': 0.001}
        rows = []
        for universe in ('A', 'B'):
            for strategy in ('long-short', 'long-only winners'):
                pick = table[
                    (table['universe'] == universe)
                    & (table['strategy'] == strategy)
                    & (table['impact_cost'].round(4) == impact[universe])
                ].iloc[0]
                zero = table[
                    (table['universe'] == universe)
                    & (table['strategy'] == strategy)
                    & (table['impact_cost'] == 0.0)
                ].iloc[0]
                excess = '-'
                alpha = '-'
                if strategy == 'long-only winners':
                    excess = self.markdown.percent(pick['excess_annual'], 1)
                    alpha = (
                        f'{self.markdown.percent(pick["alpha_monthly"])} '
                        f'(t {self.markdown.number(pick["alpha_t"], 1)})'
                    )
                rows.append(
                    [
                        universe,
                        strategy,
                        self.markdown.percent(pick['gross_mean']),
                        self.markdown.percent(pick['net_mean']),
                        self.markdown.number(pick['net_t_nw'], 1),
                        self.markdown.percent(zero['net_cagr'], 1),
                        self.markdown.percent(pick['net_cagr'], 1),
                        excess,
                        alpha,
                        self.markdown.percent(pick['max_drawdown'], 0),
                        self.markdown.number(pick['turnover'], 2),
                    ]
                )
        header = [
            'Universe',
            'Portfolio',
            'Gross mean/month',
            'Net mean/month',
            'Newey-West t (net)',
            'CAGR before costs',
            'CAGR after costs',
            'Excess over NIFTY 500 TRI a year',
            'Alpha a month after risk-free (t)',
            'Worst drawdown',
            'Turnover a month',
        ]
        text = '# Results\n\n'
        text += (
            '## Headline: 6-month ranking, 6-month holding, no skipped week\n\n'
            'This strategy was fixed as the headline in the approved plan '
            '(commit 434bcff) before any result was seen. Holding months '
            'January 2007 to September 2026, 237 months. Costs use '
            "brahmagupta's 2026 NSE delivery rates with market impact of "
            '0.3% a side for universe A (every share) and 0.1% for universe B '
            '(the liquid 500). The long-short portfolio is a paper '
            'portfolio: Indian investors cannot short cash shares overnight, '
            'and no borrowing cost is charged.\n\n'
        )
        text += self.markdown.render(header, rows)
        benchmark = table['benchmark_cagr'].dropna().iloc[0]
        text += (
            f'\nThe NIFTY 500 total return index compounded at '
            f'{self.markdown.percent(benchmark, 1)} a year over the same '
            'months.\n'
        )
        return text

    def findings(self) -> str:
        """Writes the numbered findings, with numbers taken from the tables.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = self.read('table_one')
        pick = {
            universe: grid[
                (grid['universe'] == universe)
                & (~grid['skip'])
                & (grid['J'] == 6)
                & (grid['K'] == 6)
            ].iloc[0]
            for universe in ('A', 'B')
        }
        headline = self.read('headline_strategies')
        long_only = headline[
            (headline['universe'] == 'B')
            & (headline['strategy'] == 'long-only winners')
            & (headline['impact_cost'].round(4) == 0.001)
        ].iloc[0]
        two = self.read('table_two')
        betas = {
            universe: two[
                (two['universe'] == universe) & (two['portfolio'] == 'P10-P1')
            ]['beta'].iloc[0]
            for universe in ('A', 'B')
        }
        seven = self.read('table_seven')
        cumulative = {
            universe: seven[
                (seven['universe'] == universe)
                & (seven['month'].isin([12, 36]))
            ].set_index('month')['cumulative']
            for universe in ('A', 'B')
        }
        calendar = self.read('table_four_five')
        months = {
            universe: calendar[
                (calendar['universe'] == universe)
                & (calendar['subsample'] == 'All')
            ].set_index('months')['mean']
            for universe in ('A', 'B')
        }
        periods = self.read('table_six')
        early = {
            universe: periods[
                (periods['universe'] == universe)
                & (periods['subsample'] == 'All')
                & (periods['months'] == 'All')
                & (periods['subperiod'] == '2007-2011')
            ]['t'].iloc[0]
            for universe in ('A', 'B')
        }
        pct = self.markdown.percent
        num = self.markdown.number
        return (
            '\n## What the Indian data says\n\n'
            f'1. **Momentum is strong in Indian shares.** All 64 long-short '
            f'strategies earn a positive mean before and after costs. The 6/6 '
            f'strategy with no skip earns {pct(pick["A"]["bs_mean"])} a month '
            f'in universe A (ordinary t {num(pick["A"]["bs_t_ols"], 1)}) and '
            f'{pct(pick["B"]["bs_mean"])} in universe B (t '
            f"{num(pick['B']['bs_t_ols'], 1)}), against the paper's 0.95% "
            f'(t 3.07). Skipping a week raises returns, as in the paper.\n'
            f'2. **Costs take {pct(1 - pick["A"]["bs_net_mean"] / pick["A"]["bs_mean"], 0)} '
            f'of the long-short return in universe A and '
            f'{pct(1 - pick["B"]["bs_net_mean"] / pick["B"]["bs_mean"], 0)} in '
            f"universe B, not all of it.** After brahmagupta's delivery costs "
            f'the 6/6 spread is {pct(pick["A"]["bs_net_mean"])} (A) and '
            f'{pct(pick["B"]["bs_net_mean"])} (B) a month, with Newey-West t of '
            f'{num(pick["A"]["bs_net_t_nw"], 1)} and '
            f'{num(pick["B"]["bs_net_t_nw"], 1)}. Turnover is high, '
            f'{num(pick["B"]["bs_turnover"], 2)} of the book a month, and '
            f'drawdowns are deep.\n'
            f"3. **The profit is not market risk.** The spread's beta is "
            f'{num(betas["A"])} (A) and {num(betas["B"])} (B), negative as in '
            f'the paper (-0.08), so alphas are larger than raw returns.\n'
            f'4. **The winners carry the signal, as in the paper.** Winners earn {pct(pick["B"]["buy_mean"])} '
            f'a month in universe B (t {num(pick["B"]["buy_t_ols"], 1)}) and '
            f'losers {pct(pick["B"]["sell_mean"])} (t '
            f'{num(pick["B"]["sell_t_ols"], 1)}); the loser leg is not '
            f'significantly different from zero, matching the paper, where '
            f'the abnormal return comes from the buy side.\n'
            f"5. **No January effect, but a strong March.** The paper's "
            f'January loss does not appear: January is '
            f'{pct(months["A"]["Jan"])} (A) and {pct(months["B"]["Jan"])} (B). '
            f"India's financial year ends in March, which averages "
            f'{pct(months["A"]["Mar"])} (A) and {pct(months["B"]["Mar"])} (B), '
            f'with July and October also strong and April and December '
            f'negative. Without March the spread is still positive (see the '
            f'robustness table).\n'
            f'6. **The effect was weak in 2007-2011** (ordinary t '
            f'{num(early["A"], 1)} in A and {num(early["B"], 1)} in B, '
            f'including the 2009 momentum crash) and stronger later '
            f'(Table VI).\n'
            f'7. **No long-run reversal in the main sample.** The cumulative '
            f'spread is {pct(cumulative["A"][12], 1)} (A) and '
            f'{pct(cumulative["B"][12], 1)} (B) after 12 months and '
            f'{pct(cumulative["A"][36], 1)} and {pct(cumulative["B"][36], 1)} '
            f'after 36, where the paper loses about half. The 1997-2006 '
            f'sample for universe A does reverse (Table VII below).\n'
            f"8. **Announcement returns follow the paper's shape:** winners "
            f'beat losers around results in the first months after ranking '
            f'and lose to them in months 8 to 20 (Table IX).\n'
            f'9. **A long-only investor could have held it.** Winners '
            f'decile, universe B, 6/6: {pct(long_only["net_cagr"], 1)} a '
            f'year after costs against {pct(long_only["benchmark_cagr"], 1)} '
            f'for the NIFTY 500 total return, with a beta of '
            f'{num(long_only["beta"])} and a worst drawdown of '
            f'{pct(long_only["max_drawdown"], 0)}. The alpha over the '
            f'risk-free rate is {pct(long_only["alpha_monthly"])} a month, '
            f'about {pct(long_only["alpha_monthly"] * 12, 1)} a year, but its '
            f't-statistic is only {num(long_only["alpha_t"], 1)} '
            f'(months to December 2025).\n'
        )

    def caveats(self) -> str:
        """Writes the caveats.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        return (
            '\n## Caveats\n\n'
            '- **Shorting is not possible for most Indian investors.** The '
            'long-short numbers are for a paper portfolio and charge no '
            'borrowing cost. Only the long-only results are investable.\n'
            '- **Costs are 2026 rates applied to the whole sample.** '
            'Securities transaction tax and brokerage were higher in 2007. '
            'Market impact (0.3% and 0.1% a side) is an assumption.\n'
            '- **Delisted shares are in the data, but their last trade is '
            'the last return.** Losses after it are not charged; see the '
            'delisting stress.\n'
            "- **Corporate actions are incomplete.** NSE's list is reliable "
            'only from 2005; some bonuses are missing (an unadjusted 1:2 '
            'bonus is a -33% day that the cleaning rule does not catch) and '
            'genuine one-day falls beyond -50% were set to zero. Renamed '
            'shares appear as one share ending and another starting. '
            'Rights issues, mergers and demergers are not adjusted.\n'
            '- **Universe A includes penny stocks,** with monthly returns '
            'above 300% in the late 1990s. Universe B excludes them by '
            'construction.\n'
            '- **Size is a proxy.** Before February 2024 there is no free '
            'market-capitalisation series, so size terciles use median '
            'daily traded value.\n'
            '- **The risk-free rate stops in December 2025** and results '
            'announcements stop in March 2025, so alphas and Table IX use '
            'shorter samples.\n'
            "- **The sample is 237 months,** against the paper's 300, and the "
            'strongest evidence is after 2011.\n'
            '- **The skipped week is implemented as holding that starts five '
            'sessions after ranking,** which is what the paper describes; the '
            'plan wrote it the other way round, with the ranking ending five '
            'sessions earlier. The two are equivalent in what they avoid.\n'
        )

    def variants(self) -> str:
        """Counts the variants tried and the strategies that pass a cutoff.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = self.read('table_one')
        cutoff = stats.norm.isf(0.05 / len(grid) / 2.0)
        passing = int((grid['bs_t_nw'] > cutoff).sum())
        positive = int((grid['bs_mean'] > 0).sum())
        net_positive = int((grid['bs_net_mean'] > 0).sum())
        return (
            '\n## How many variants were tried\n\n'
            f'Table I runs {len(grid)} strategies: 32 J/K combinations on '
            'each of 2 universes (16 with and 16 without the skipped week '
            'per universe). Each is scored long-short and long-only, so '
            f'{2 * len(grid)} series are scored. {positive} of {len(grid)} '
            f'long-short strategies have a positive mean before costs and '
            f'{net_positive} after costs. With {len(grid)} tests, a '
            f'Bonferroni cutoff for a 5% two-sided level is |t| > '
            f'{cutoff:.2f}; {passing} of {len(grid)} pass on Newey-West '
            't-statistics. The 64 strategies are highly correlated, so this '
            'cutoff is conservative. Tables II to IX use only the 6/6 '
            'strategy. The robustness checks add 6 variants for each of 2 '
            'universes and the delisting stress 4 treatments for each. No '
            'parameter was tuned on results.\n'
        )

    def table_one(self) -> str:
        """Writes Table I for India beside the paper's.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = self.read('table_one')
        paper = pd.read_csv(self.paper / 'paper_table_i.csv')
        paper = paper[paper['leg'] == 'buy_sell']
        text = (
            '\n## Table I: buy-minus-sell returns of the 32 strategies\n\n'
            'Paper: NYSE and AMEX, 1965-1989 (page 70). India: NSE, '
            '2007-2026. Cells give the mean monthly return before costs '
            'with its ordinary t-statistic, as the paper reports, and the '
            "paper's value after the bar. Second tables give the return "
            'after costs with the Newey-West t-statistic.\n'
        )
        for universe in ('A', 'B'):
            for skip in (False, True):
                subset = grid[
                    (grid['universe'] == universe) & (grid['skip'] == skip)
                ]
                panel = 'B' if skip else 'A'
                reference = paper[paper['panel'] == panel]
                text += f'\n**Universe {universe}, '
                text += 'one week skipped' if skip else 'no skip'
                text += '**\n\n'
                gross_rows = []
                net_rows = []
                for ranking in (3, 6, 9, 12):
                    gross_row = [f'J={ranking}']
                    net_row = [f'J={ranking}']
                    for holding in (3, 6, 9, 12):
                        pick = subset[
                            (subset['J'] == ranking) & (subset['K'] == holding)
                        ].iloc[0]
                        old = reference[
                            (reference['J'] == ranking)
                            & (reference['K'] == holding)
                        ].iloc[0]
                        gross_row.append(
                            f'{self.markdown.percent(pick["bs_mean"])} '
                            f'(t {self.markdown.number(pick["bs_t_ols"], 1)}) '
                            f'\\| {self.markdown.percent(old["mean_monthly_return"])}'
                        )
                        net_row.append(
                            f'{self.markdown.percent(pick["bs_net_mean"])} '
                            f'(t {self.markdown.number(pick["bs_t_nw"] * 0 + pick["bs_net_t_nw"], 1)})'
                        )
                    gross_rows.append(gross_row)
                    net_rows.append(net_row)
                header = ['', 'K=3', 'K=6', 'K=9', 'K=12']
                text += 'Before costs | paper:\n\n'
                text += self.markdown.render(header, gross_rows)
                text += '\nAfter costs, Newey-West t:\n\n'
                text += self.markdown.render(header, net_rows)
        return text

    def long_only_grid(self) -> str:
        """Writes the long-only results of all strategies in universe B.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = self.read('table_one')
        text = (
            '\n## Long-only winners, universe B, after costs\n\n'
            'Compound annual return after costs, with the excess over the '
            'NIFTY 500 total return in brackets. Worst drawdowns are in '
            '`table_one.csv`.\n'
        )
        for skip in (False, True):
            subset = grid[(grid['universe'] == 'B') & (grid['skip'] == skip)]
            rows = []
            for ranking in (3, 6, 9, 12):
                row = [f'J={ranking}']
                for holding in (3, 6, 9, 12):
                    pick = subset[
                        (subset['J'] == ranking) & (subset['K'] == holding)
                    ].iloc[0]
                    row.append(
                        f'{self.markdown.percent(pick["lo_net_cagr"], 1)} '
                        f'({self.markdown.percent(pick["lo_net_excess_annual"], 1)})'
                    )
                rows.append(row)
            text += (
                '\n' + ('One week skipped:' if skip else 'No skip:') + '\n\n'
            )
            text += self.markdown.render(
                ['', 'K=3', 'K=6', 'K=9', 'K=12'], rows
            )
        return text

    def tables_two_three(self) -> str:
        """Writes Tables II and III.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        two = self.read('table_two')
        three = self.read('table_three')
        text = '\n## Table II: betas of the 6/6 deciles (page 73)\n\n'
        rows = []
        for universe in ('A', 'B'):
            subset = two[two['universe'] == universe].set_index('portfolio')
            row = [f'India {universe}']
            for name in ('1', '2', '5', '9', '10', 'P10-P1'):
                row.append(self.markdown.number(subset.loc[name, 'beta']))
            rows.append(row)
        paper_row = ['Paper']
        for name in ('1', '2', '5', '9', '10', 'P10-P1'):
            paper_row.append(
                self.markdown.number(PaperNumbers.TABLE_II_BETA[name])
            )
        rows.append(paper_row)
        text += self.markdown.render(
            ['', 'P1 (losers)', 'P2', 'P5', 'P9', 'P10 (winners)', 'P10-P1'],
            rows,
        )
        text += (
            '\nBetas are against the NIFTY 500 total return. The paper '
            'also reports average market capitalisation; India has no free '
            'market-cap history before February 2024, so `table_two.csv` '
            'gives the median daily traded value in crore rupees instead.\n'
        )
        text += '\n## Table III: 6/6 spread by size and beta subsample (page 78)\n\n'
        rows = []
        for universe in ('A', 'B'):
            subset = three[
                (three['universe'] == universe)
                & (three['portfolio'] == 'P10-P1')
            ]
            subset = subset.set_index('subsample')
            row = [f'India {universe}']
            for name in PaperNumbers.TABLE_III_ALL_P10_P1:
                pick = subset.loc[name]
                row.append(
                    f'{self.markdown.percent(pick["mean"])} '
                    f'(t {self.markdown.number(pick["t"], 1)})'
                )
            rows.append(row)
        row = ['Paper']
        for name, value in PaperNumbers.TABLE_III_ALL_P10_P1.items():
            row.append(self.markdown.percent(value))
        rows.append(row)
        text += self.markdown.render(
            [
                '',
                'All',
                'S1 small',
                'S2',
                'S3 large',
                'B1 low beta',
                'B2',
                'B3 high beta',
            ],
            rows,
        )
        text += (
            '\nSize subsamples are thirds of the median daily traded value, '
            'a proxy for size. Alphas against the NIFTY 500 total return '
            'excess of the risk-free rate (months to December 2025) are in '
            '`table_three.csv`.\n'
        )
        return text

    def tables_four_to_six(self) -> str:
        """Writes Tables IV, V and VI.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        four = self.read('table_four_five')
        six = self.read('table_six')
        text = '\n## Tables IV and V: 6/6 spread by calendar month (pages 80-81)\n\n'
        rows = []
        names = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
            'Feb-Dec',
        ]
        for name in names:
            row = [name]
            for universe in ('A', 'B'):
                pick = four[
                    (four['universe'] == universe)
                    & (four['subsample'] == 'All')
                    & (four['months'] == name)
                ].iloc[0]
                row.append(
                    f'{self.markdown.percent(pick["mean"])} '
                    f'(t {self.markdown.number(pick["t"], 1)}, '
                    f'{self.markdown.number(pick["positive_share"] * 100, 0)}% up)'
                )
            row.append(self.markdown.percent(PaperNumbers.TABLE_IV[name]))
            rows.append(row)
        text += self.markdown.render(
            ['Month', 'India A', 'India B', 'Paper'],
            rows,
        )
        text += (
            '\nThe paper finds a large negative January (-6.9%, positive in '
            'only 24% of years). India has no such January effect. March, '
            'July and October are the strongest months, March being the end '
            'of the Indian financial year, and April and December are '
            'negative. With 20 observations a month, single months are '
            'noisy.\n'
        )
        text += '\n## Table VI: 6/6 spread by subperiod (page 82)\n\n'
        rows = []
        for months in ('All', 'All except Mar'):
            for universe in ('A', 'B'):
                row = [f'{months}, India {universe}']
                for period in (
                    '2007-2011',
                    '2012-2016',
                    '2017-2021',
                    '2022-2026',
                ):
                    pick = six[
                        (six['universe'] == universe)
                        & (six['subsample'] == 'All')
                        & (six['months'] == months)
                        & (six['subperiod'] == period)
                    ].iloc[0]
                    row.append(
                        f'{self.markdown.percent(pick["mean"])} '
                        f'(t {self.markdown.number(pick["t"], 1)})'
                    )
                rows.append(row)
        text += self.markdown.render(
            ['', '2007-11', '2012-16', '2017-21', '2022-Sep 26'],
            rows,
        )
        paper = ', '.join(
            f'{name} {self.markdown.percent(value)}'
            for name, value in PaperNumbers.TABLE_VI.items()
        )
        text += f'\nPaper, all months, 1965-1989: {paper}.\n'
        return text

    def tables_seven_eight(self) -> str:
        """Writes Tables VII and VIII.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        text = '\n## Table VII: event time, cumulative 6/6 spread (page 84)\n\n'
        text += (
            'Cumulative winners-minus-losers return (sum of monthly averages) '
            'after 6, 12, 24 and 36 months with Newey-West t-statistics. '
            'Main sample: formation months December 2006 to September 2023.\n\n'
        )
        rows = []
        for name, label in (
            ('table_seven', 'India, 2007-2026'),
            (
                'table_eight_early_sample',
                'India early sample, 1997-2006 (Table VIII stand-in)',
            ),
        ):
            table = self.read(name)
            for universe in ('A', 'B'):
                subset = table[table['universe'] == universe].set_index('month')
                row = [f'{label}, {universe}']
                for months in (6, 12, 24, 36):
                    row.append(
                        f'{self.markdown.percent(subset.loc[months, "cumulative"], 1)} '
                        f'(t {self.markdown.number(subset.loc[months, "cumulative_t"], 1)})'
                    )
                rows.append(row)
        paper_row = ['Paper, 1965-1989']
        for months in (6, 12, 24, 36):
            paper_row.append(
                self.markdown.percent(
                    PaperNumbers.TABLE_VII_CUMULATIVE[months], 1
                )
            )
        rows.append(paper_row)
        text += self.markdown.render(['', '6 months', '12', '24', '36'], rows)
        text += (
            '\nThe paper finds that about half the first-year profit is '
            'lost in the next two years. In the main Indian sample the '
            'profit does not reverse; in the 1997-2006 sample it does for '
            'universe A. The early sample has less reliable corporate '
            'action data and many penny stocks, and stands in for the '
            "paper's pre-1965 back-test (Table VIII) only loosely.\n"
        )
        return text

    def section_three(self) -> str:
        """Writes the Section III results.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        table = self.read('section_three')
        text = '\n## Section III: sources of the profits (pages 70-75)\n\n'
        rows = []
        for quantity in PaperNumbers.SECTION_III:
            row = [quantity]
            for universe in ('A', 'B'):
                pick = table[
                    (table['universe'] == universe)
                    & (table['quantity'] == quantity)
                ].iloc[0]
                value = self.markdown.number(pick['value'], 4)
                if pick['t'] == pick['t']:
                    value += f' (t {self.markdown.number(pick["t"], 2)})'
                row.append(value)
            row.append(
                self.markdown.number(PaperNumbers.SECTION_III[quantity], 4)
            )
            rows.append(row)
        text += self.markdown.render(['', 'India A', 'India B', 'Paper'], rows)
        return text

    def table_nine(self) -> str:
        """Writes Table IX.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        table = self.read('table_nine')
        text = '\n## Table IX: announcement-period returns (page 88)\n\n'
        text += (
            'Winners minus losers, 3-day return around quarterly results, '
            'by months since ranking. India: NSE results filings, August '
            "2007 to March 2025 (NSE's results feed is nearly empty after "
            'that).\n\n'
        )
        rows = []
        for universe in ('A', 'B'):
            subset = table[table['universe'] == universe].set_index('t')
            first = subset.loc[1:6, 'winners_minus_losers'].mean()
            middle = subset.loc[8:20, 'winners_minus_losers'].mean()
            late = subset.loc[11:18, 'winners_minus_losers'].mean()
            rows.append(
                [
                    f'India {universe}',
                    self.markdown.percent(first),
                    self.markdown.percent(middle),
                    self.markdown.percent(late),
                ]
            )
        rows.append(
            [
                'Paper',
                self.markdown.percent(PaperNumbers.TABLE_IX_FIRST_SIX_MONTHS),
                '-',
                self.markdown.percent(PaperNumbers.TABLE_IX_MONTHS_11_TO_18),
            ]
        )
        text += self.markdown.render(
            [
                '',
                'Months 1-6 average',
                'Months 8-20 average',
                'Months 11-18 average',
            ],
            rows,
        )
        return text

    def robustness(self) -> str:
        """Writes the robustness and delisting stress results.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        table = self.read('robustness')
        text = '\n## Robustness of the 6/6 long-short spread\n\n'
        rows = []
        for variant in table['variant'].unique():
            row = [variant]
            for universe in ('A', 'B'):
                subset = table[
                    (table['universe'] == universe)
                    & (table['variant'] == variant)
                ]
                gross = subset[subset['return'] == 'gross'].iloc[0]
                net = subset[subset['return'] == 'net'].iloc[0]
                double = subset[
                    subset['return'] == 'net at double impact'
                ].iloc[0]
                row.append(
                    f'{self.markdown.percent(gross["mean"])} '
                    f'(t {self.markdown.number(gross["t_nw"], 1)})'
                )
                row.append(self.markdown.percent(net['mean']))
                row.append(self.markdown.percent(double['mean']))
            rows.append(row)
        text += self.markdown.render(
            [
                'Variant',
                'A gross (NW t)',
                'A net',
                'A net, double impact',
                'B gross (NW t)',
                'B net',
                'B net, double impact',
            ],
            rows,
        )
        stress = self.read('delisting_stress')
        text += (
            "\n**Delisting stress.** The bhavcopies give a share's last "
            'close but not what holders received on delisting, so nothing is '
            'charged after the last trade. As an extreme bound, a loss of '
            '100% is charged in the month after the last return of every '
            'share that disappears for good (many such exits are mergers or '
            'symbol changes, so this overstates the harm). Mean monthly '
            'long-short return, before costs:\n\n'
        )
        rows = []
        for treatment in ('none', 'both legs', 'losers only', 'winners only'):
            row = [treatment]
            for universe in ('A', 'B'):
                pick = stress[
                    (stress['universe'] == universe)
                    & (stress['treatment'] == treatment)
                ].iloc[0]
                row.append(
                    f'{self.markdown.percent(pick["mean"])} '
                    f'(NW t {self.markdown.number(pick["t_nw"], 1)})'
                )
            rows.append(row)
        text += self.markdown.render(['Exit loss charged to', 'A', 'B'], rows)
        return text

    def cross_check(self) -> str:
        """Writes the check against the IIMA momentum factor.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        table = self.read('cross_check_iima')
        text = '\n## Cross-check with the IIMA momentum factor\n\n'
        rows = []
        for universe in ('A', 'B'):
            subset = table[table['strategy'].str.startswith(universe + '_')]
            headline = subset[
                subset['strategy'] == f'{universe}_noskip_6_6'
            ].iloc[0]
            rows.append(
                [
                    universe,
                    self.markdown.number(
                        headline['correlation_with_iima_wml'], 2
                    ),
                    self.markdown.number(
                        subset['correlation_with_iima_wml'].min(), 2
                    ),
                    self.markdown.number(
                        subset['correlation_with_iima_wml'].max(), 2
                    ),
                    self.markdown.percent(headline['our_mean']),
                    self.markdown.percent(headline['iima_mean']),
                ]
            )
        text += (
            'Correlation of each monthly long-short series with the IIMA '
            'Indian WML factor (Agarwalla, Jacob and Varma), built '
            'independently from CMIE Prowess data, January 2007 to '
            'December 2025.\n\n'
        )
        text += self.markdown.render(
            [
                'Universe',
                'Correlation, 6/6 no skip',
                'Lowest over 32 strategies',
                'Highest',
                'Our 6/6 mean',
                'IIMA mean',
            ],
            rows,
        )
        return text
