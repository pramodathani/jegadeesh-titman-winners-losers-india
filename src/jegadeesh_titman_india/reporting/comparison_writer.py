"""Compares this study's tables with the earlier study's."""

import pathlib

import pandas as pd

from jegadeesh_titman_india.reporting.markdown_table import MarkdownTable


class ComparisonWriter:
    """Writes results/comparison.md.

    Attributes:
        mine: This study's results folder.
        theirs: The earlier study's results folder, read only.
        markdown: The table formatter.
    """

    PAIRS: tuple[tuple[str, str], ...] = (
        ('A', 'all_shares'),
        ('B', 'most_traded_500'),
    )

    def __init__(self, mine: pathlib.Path, theirs: pathlib.Path) -> None:
        """Creates the writer.

        Args:
            mine: This study's results folder.
            theirs: The earlier study's bhavcopy_from_2005 results folder
                and its parent, given as the results folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.mine = mine
        self.theirs = theirs
        self.markdown = MarkdownTable()

    def write(self) -> None:
        """Writes the comparison.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        parts = [
            self.opening(),
            self.table_one(),
            self.skip_variant(),
            self.long_only(),
            self.calendar(),
            self.event_time(),
            self.betas(),
            self.differences(),
        ]
        (self.mine / 'comparison.md').write_text('\n'.join(parts))

    def opening(self) -> str:
        """Writes the opening paragraph.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        return (
            '# Comparison with the earlier study\n\n'
            'This study is set beside the earlier study of the same paper '
            '(github.com/pramodathani/jegadeesh-titman-momentum-india, '
            'results in `results/bhavcopy_from_2005`). I read the earlier '
            "study's result tables and README only after my own results "
            'were written and committed (commit 9e8bd55), and its code only '
            'for how it implements the skipped week (see below). I changed '
            'none of my main results afterwards. Both studies use the same '
            '237 holding months, January 2007 to September 2026, the same '
            'NSE bhavcopy files and corporate actions, and two universes: '
            'every share (my A, their all_shares) and the 500 most traded '
            '(my B, their most_traded_500). Differences are mine minus '
            "theirs. The earlier study's numbers come from its own CSV "
            'files, read by `scripts/compare_with_earlier_study.py`.\n'
        )

    def read_theirs(self, name: str) -> pd.DataFrame:
        """Reads one of the earlier study's tables.

        Args:
            name: The file name without the extension.

        Returns:
            The table.

        Raises:
            None.
        """
        return pd.read_csv(self.theirs / 'bhavcopy_from_2005' / f'{name}.csv')

    def table_one(self) -> str:
        """Compares the 32 long-short spreads and the legs.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = pd.read_csv(self.mine / 'table_one.csv')
        text = '## Table I: monthly mean of buy minus sell, before costs\n\n'
        rows = []
        legs = []
        for mine_name, their_name in self.PAIRS:
            theirs = self.read_theirs(f'{their_name}_table_1_all_strategies')
            for skip in (False, True):
                days = 5 if skip else 0
                mine = grid[
                    (grid['universe'] == mine_name) & (grid['skip'] == skip)
                ]
                other = theirs[
                    (theirs['skipped_days'] == days)
                    & (theirs['portfolio'] == 'buy_minus_sell')
                ]
                joined = mine.merge(
                    other,
                    left_on=['J', 'K'],
                    right_on=['ranking_months', 'holding_months'],
                )
                difference = joined['bs_mean'] - joined['mean']
                correlation = joined['bs_mean'].corr(joined['mean'])
                mine_positive = int((joined['bs_mean'] > 0).sum())
                their_positive = int((joined['mean'] > 0).sum())
                positive_text = f'{mine_positive}/16 and {their_positive}/16'
                rows.append(
                    [
                        f'{mine_name} vs {their_name}',
                        'skip' if skip else 'no skip',
                        self.markdown.percent(joined['bs_mean'].mean()),
                        self.markdown.percent(joined['mean'].mean()),
                        self.markdown.percent(difference.mean()),
                        self.markdown.percent(difference.abs().max()),
                        self.markdown.number(correlation, 3),
                        positive_text,
                    ]
                )
            pick = grid[
                (grid['universe'] == mine_name)
                & (~grid['skip'])
                & (grid['J'] == 6)
                & (grid['K'] == 6)
            ].iloc[0]
            for leg, column in (
                ('buy', 'buy_mean'),
                ('sell', 'sell_mean'),
                ('buy_minus_sell', 'bs_mean'),
            ):
                value = theirs[
                    (theirs['skipped_days'] == 0)
                    & (theirs['ranking_months'] == 6)
                    & (theirs['holding_months'] == 6)
                    & (theirs['portfolio'] == leg)
                ]['mean'].iloc[0]
                legs.append(
                    [
                        mine_name,
                        leg,
                        self.markdown.percent(pick[column]),
                        self.markdown.percent(value),
                        self.markdown.percent(pick[column] - value),
                    ]
                )
        text += self.markdown.render(
            [
                'Universe',
                'Panel',
                'My average of 16',
                'Their average',
                'Mean difference',
                'Largest cell difference',
                'Correlation of the 16 cells',
                'Positive cells (mine and theirs)',
            ],
            rows,
        )
        text += '\nThe 6/6 strategy without a skip, both legs:\n\n'
        text += self.markdown.render(
            ['Universe', 'Leg', 'Mine', 'Theirs', 'Difference'],
            legs,
        )
        return text

    def skip_variant(self) -> str:
        """Compares the skip panel under both ways of leaving the gap.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        grid = pd.read_csv(self.mine / 'table_one.csv')
        variant = pd.read_csv(self.mine / 'table_one_earlier_ranking_skip.csv')
        rows = []
        for mine_name, their_name in self.PAIRS:
            theirs = self.read_theirs(f'{their_name}_table_1_all_strategies')
            theirs = theirs[
                (theirs['portfolio'] == 'buy_minus_sell')
                & (theirs['skipped_days'] == 5)
            ]
            own = variant[variant['universe'] == mine_name]
            joined = own.merge(
                theirs,
                left_on=['J', 'K'],
                right_on=['ranking_months', 'holding_months'],
            )
            main_skip = grid[(grid['universe'] == mine_name) & (grid['skip'])][
                'bs_mean'
            ].mean()
            no_skip = grid[(grid['universe'] == mine_name) & (~grid['skip'])][
                'bs_mean'
            ].mean()
            rows.append(
                [
                    f'{mine_name} vs {their_name}',
                    self.markdown.percent(no_skip, 3),
                    self.markdown.percent(main_skip, 3),
                    self.markdown.percent(joined['mean_x'].mean(), 3),
                    self.markdown.percent(joined['mean_y'].mean(), 3),
                    self.markdown.number(
                        joined['mean_x'].corr(joined['mean_y']), 3
                    ),
                ]
            )
        text = '\n## The skipped week\n\n'
        text += (
            'My main skip panel ranks at the calendar month end and starts '
            "holding five sessions later. After reading the earlier study's "
            'code for this one point, I found that it instead ends the '
            'ranking window five sessions before the month end and holds '
            'calendar months. Both leave five sessions between the end of '
            'the ranking window and the first day of holding, but the '
            'skipped week falls in different parts of the calendar month. '
            'I added the second way as an extra check (`table_one_earlier_'
            'ranking_skip.csv`, run after seeing the comparison; it does '
            "not replace the plan's version). Average of the 16 "
            'buy-minus-sell means:\n\n'
        )
        text += self.markdown.render(
            [
                'Universe',
                'Mine, no skip',
                'Mine, skip after ranking (main)',
                'Mine, ranking window ended early',
                'Theirs, skip',
                'Correlation of the 16 cells, early ending vs theirs',
            ],
            rows,
        )
        text += (
            '\nWith their way of leaving the gap my results agree with '
            'theirs; with mine the gap raises the spread by 0.16 points a '
            "month in universe A. So the paper's finding that a skipped "
            'week raises returns holds or fails in India depending on where '
            "in the calendar month the week falls, and neither study's "
            'statement about the skip is wrong. The "does not help" '
            'conclusion in the earlier README belongs to its way of leaving '
            'the gap.\n'
        )
        return text

    def long_only(self) -> str:
        """Compares the long-only portfolios in the liquid universe.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        mine = pd.read_csv(self.mine / 'table_one.csv')
        theirs = pd.read_csv(
            self.theirs / 'portfolio_comparison' / 'bhavcopy_from_2005.csv'
        )
        theirs = theirs[theirs['universe'] == 'most_traded_500']
        mine = mine[mine['universe'] == 'B']
        joined = mine.assign(
            skipped_days=mine['skip'].map({True: 5, False: 0})
        ).merge(
            theirs,
            left_on=['J', 'K', 'skipped_days'],
            right_on=['ranking_months', 'holding_months', 'skipped_days'],
        )
        difference = joined['lo_net_cagr'] - joined['compound_annual']
        best_mine = joined.sort_values('lo_net_cagr').iloc[-1]
        best_theirs = joined.sort_values('compound_annual').iloc[-1]
        six = joined[
            (joined['J'] == 6)
            & (joined['K'] == 6)
            & (joined['skipped_days'] == 0)
        ].iloc[0]
        mine_skip = 'skip' if best_mine['skip'] else 'no skip'
        their_skip = 'skip' if best_theirs['skipped_days'] else 'no skip'
        best_mine_text = (
            f'{self.markdown.percent(best_mine["lo_net_cagr"], 1)} '
            f'(J{int(best_mine["J"])}/K{int(best_mine["K"])}, {mine_skip})'
        )
        best_theirs_text = (
            f'{self.markdown.percent(best_theirs["compound_annual"], 1)} '
            f'(J{int(best_theirs["J"])}/K{int(best_theirs["K"])}, {their_skip})'
        )
        text = '\n## Long-only winners in the liquid 500, after costs\n\n'
        text += self.markdown.render(
            ['', 'Mine', 'Theirs'],
            [
                [
                    'Average compound annual return of the 32 portfolios',
                    self.markdown.percent(joined['lo_net_cagr'].mean(), 1),
                    self.markdown.percent(joined['compound_annual'].mean(), 1),
                ],
                [
                    'Correlation across the 32 portfolios',
                    self.markdown.number(
                        joined['lo_net_cagr'].corr(joined['compound_annual']), 3
                    ),
                    '',
                ],
                [
                    'Highest compound annual return',
                    best_mine_text,
                    best_theirs_text,
                ],
                [
                    '6/6 without skip, compound annual return',
                    self.markdown.percent(six['lo_net_cagr'], 1),
                    self.markdown.percent(six['compound_annual'], 1),
                ],
                [
                    '6/6 without skip, worst drawdown',
                    self.markdown.percent(six['lo_net_max_drawdown'], 0),
                    self.markdown.percent(six['maximum_drawdown'], 0),
                ],
                [
                    'Benchmark compound annual return',
                    self.markdown.percent(six['benchmark_cagr'], 1)
                    + ' (NIFTY 500 total return index)',
                    self.markdown.percent(six['benchmark_compound_annual'], 1)
                    + ' (price index plus dividend yield)',
                ],
                [
                    'Mean difference mine minus theirs, 32 portfolios',
                    self.markdown.percent(difference.mean(), 2),
                    '',
                ],
            ],
        )
        return text

    def calendar(self) -> str:
        """Compares the calendar-month spreads of the 6/6 strategy.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        mine = pd.read_csv(self.mine / 'table_four_five.csv')
        text = (
            '\n## Calendar months, 6/6 spread (my Table IV, their table 4)\n\n'
        )
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
        ]
        for mine_name, their_name in self.PAIRS:
            theirs = self.read_theirs(f'{their_name}_table_4_calendar_months')
            rows = []
            differences = []
            for number, name in enumerate(names, start=1):
                mine_value = mine[
                    (mine['universe'] == mine_name)
                    & (mine['subsample'] == 'All')
                    & (mine['months'] == name)
                ]['mean'].iloc[0]
                their_value = theirs[
                    theirs['calendar_month'].astype(str) == str(number)
                ]['mean'].iloc[0]
                differences.append(mine_value - their_value)
                rows.append(
                    [
                        name,
                        self.markdown.percent(mine_value),
                        self.markdown.percent(their_value),
                    ]
                )
            text += f'\nUniverse {mine_name} against {their_name}; largest monthly difference {self.markdown.percent(max(abs(value) for value in differences))}:\n\n'
            text += self.markdown.render(['Month', 'Mine', 'Theirs'], rows)
        return text

    def event_time(self) -> str:
        """Compares cumulative event-time returns.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        mine = pd.read_csv(self.mine / 'table_seven.csv')
        text = '\n## Event time, cumulative spread (my Table VII, their table 7)\n\n'
        rows = []
        for mine_name, their_name in self.PAIRS:
            theirs = self.read_theirs(
                f'{their_name}_table_7_event_time'
            ).set_index('event_month')
            subset = mine[mine['universe'] == mine_name].set_index('month')
            for months in (6, 12, 24, 36):
                rows.append(
                    [
                        f'{mine_name} vs {their_name}',
                        str(months),
                        self.markdown.percent(
                            subset.loc[months, 'cumulative'], 1
                        ),
                        self.markdown.percent(
                            theirs.loc[months, 'cumulative_mean'], 1
                        ),
                    ]
                )
        text += self.markdown.render(
            ['Universe', 'Event month', 'Mine', 'Theirs'],
            rows,
        )
        text += (
            '\nTheir formation months start in 2005 and mine in December '
            '2006, which accounts for part of any gap.\n'
        )
        return text

    def betas(self) -> str:
        """Compares the decile betas of the 6/6 strategy.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        mine = pd.read_csv(self.mine / 'table_two.csv')
        text = '\n## Decile betas against the NIFTY 500 (my Table II, their table 2)\n\n'
        rows = []
        for mine_name, their_name in self.PAIRS:
            theirs = self.read_theirs(
                f'{their_name}_table_2_decile_risk'
            ).set_index('portfolio')
            subset = mine[mine['universe'] == mine_name].set_index('portfolio')
            for decile in ('1', '10', 'P10-P1'):
                key = 'P' + decile if decile.isdigit() else decile
                rows.append(
                    [
                        f'{mine_name} vs {their_name}',
                        key,
                        self.markdown.number(subset.loc[decile, 'beta']),
                        self.markdown.number(theirs.loc[key, 'beta_nifty_500']),
                    ]
                )
        text += self.markdown.render(
            ['Universe', 'Portfolio', 'Mine', 'Theirs'], rows
        )
        return text

    def differences(self) -> str:
        """Lists what differs between the two studies, from their READMEs.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        return (
            '\n## What differs between the studies\n\n'
            "Taken from the earlier study's README and result files, and "
            'from my own plan:\n\n'
            '- **Data start.** Theirs starts on 2005-01-03; mine uses '
            'bhavcopies from 1995, which only adds an early sample '
            '(1997-2006) that theirs does not have; the main sample is the '
            'same 237 months.\n'
            '- **Corporate actions.** They match each split or bonus to the '
            'trading day near its listed ex-date whose price drop fits the '
            "ratio and apply it only if it brings that day's return closer "
            'to zero. I apply each action on the first trading day on or '
            'after its listed ex-date. Both set one-day returns below -50% '
            'or above +100% to zero. Their summary reports 702 such rows '
            '(709 in the README); I count 382 since 2005-01-03 and 863 '
            'over 1995-2026, counted from `data/derived/data_errors.csv`. '
            'The difference probably comes from how corporate actions are '
            'matched and from funds, which I remove; I did not check.\n'
            '- **Funds.** I remove 521 ETF, fund and entitlement symbols by '
            'ISIN or name. Their README does not say whether funds are '
            'removed, and I did not check their code for this; funds in '
            'their universe could account for part of the small gaps in the '
            'buy leg.\n'
            '- **Liquid universe.** Theirs ranks the previous six months of '
            'traded value; mine uses the previous 250 sessions with a '
            'minimum 80% trading share. Both keep 500 shares.\n'
            '- **Benchmark.** Theirs is the NIFTY 500 price index plus a '
            "twelfth of the month's dividend yield (a later-year average "
            "yield before July 2012); mine is NSE's NIFTY 500 total return "
            'index, found on niftyindices.com from 1995. The two compound at '
            '11.5% and 11.4% over the sample.\n'
            '- **Costs.** Both use 2026 statutory charges and market impact '
            'of 0.1% (liquid) and 0.3% (all). Their README notes that the '
            'fixed depository charge is not included; mine does not model '
            'it either.\n'
            '- **Risk-free rate.** Their README says none is used; mine uses '
            'the IIMA 91-day bill series to December 2025 for alphas.\n'
            '- **Paper tables.** I add Table IX (announcement returns), '
            "Section III, Table VIII's stand-in, size and beta subsamples "
            'by terciles, a delisting stress and robustness checks. They do '
            'not replicate Table IX and use liquidity terciles only.\n'
            '- **The skip.** See the section above: the two studies leave '
            'the gap in different places in the calendar month.\n'
        )
