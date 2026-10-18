"""Formats rows as a Markdown table."""

import math


class MarkdownTable:
    """Turns a header and rows into Markdown text."""

    def render(self, header: list[str], rows: list[list[str]]) -> str:
        """Builds the table.

        Args:
            header: The column titles.
            rows: The rows, each a list of strings.

        Returns:
            The Markdown text, ending in a newline.

        Raises:
            None.
        """
        lines = [
            '| ' + ' | '.join(header) + ' |',
            '|' + '|'.join(['---'] * len(header)) + '|',
        ]
        for row in rows:
            lines.append('| ' + ' | '.join(row) + ' |')
        return '\n'.join(lines) + '\n'

    def percent(self, value: float, digits: int = 2) -> str:
        """Formats a fraction as a percent.

        Args:
            value: A fraction, such as 0.0148.
            digits: Digits after the point.

        Returns:
            The text, or a dash for NaN.

        Raises:
            None.
        """
        if math.isnan(value):
            return '-'
        return f'{value * 100:.{digits}f}%'

    def number(self, value: float, digits: int = 2) -> str:
        """Formats a number.

        Args:
            value: The number.
            digits: Digits after the point.

        Returns:
            The text, or a dash for NaN.

        Raises:
            None.
        """
        if math.isnan(value):
            return '-'
        return f'{value:.{digits}f}'
