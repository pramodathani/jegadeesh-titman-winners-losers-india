"""Turns NSE corporate action lists into price factors and dividends."""

import json
import math
import pathlib
import re

import pandas as pd


class CorporateActionTable:
    """Splits, bonuses and dividends of NSE shares by ex-date."""

    NUMBER: str = r'(\d+(?:\.\d+)?)'

    def parse_subject(
        self,
        subject: str,
        face_value: float,
    ) -> tuple[float, float]:
        """Reads one action's text.

        Args:
            subject: The action's wording, such as Bonus 1:1.
            face_value: The share's face value in rupees, or NaN.

        Returns:
            A pair: the price factor and the cash dividend per share before
            the action. The factor multiplies the post-action price to make
            it comparable with the earlier price; it is 1 when the action
            does not change the price.

        Raises:
            None.
        """
        text = subject.lower()
        factor = 1.0
        dividend = 0.0
        bonus = re.search(
            r'bonus\s*' + self.NUMBER + r'\s*:\s*' + self.NUMBER, text
        )
        if bonus:
            new_shares = float(bonus.group(1))
            held_shares = float(bonus.group(2))
            if held_shares > 0:
                factor *= (new_shares + held_shares) / held_shares
        is_split = 'split' in text or 'sub-division' in text
        is_consolidation = 'consolidation' in text
        if is_split or is_consolidation:
            amounts = re.findall(r'(?:rs\.?|re\.?)\s*' + self.NUMBER, text)
            if len(amounts) >= 2:
                old_value = float(amounts[0])
                new_value = float(amounts[1])
                if old_value > 0 and new_value > 0:
                    factor *= old_value / new_value
        dividend_text = text.replace('sub-division', '').replace('division', '')
        is_dividend = 'dividend' in dividend_text or 'div' in dividend_text
        if is_dividend and 'interest' not in text:
            dividend = self._dividend(text, face_value)
        return factor, dividend

    def _dividend(self, text: str, face_value: float) -> float:
        """Reads a dividend in rupees or as a percent of face value.

        Args:
            text: The lower-case subject.
            face_value: The face value in rupees, or NaN.

        Returns:
            The dividend per share in rupees, 0 when it cannot be read.

        Raises:
            None.
        """
        percent = re.search(self.NUMBER + r'\s*%', text)
        if percent and not math.isnan(face_value):
            return float(percent.group(1)) / 100.0 * face_value
        amount = re.search(r'(?:rs\.?|re\.?)\s*' + self.NUMBER, text)
        if amount:
            return float(amount.group(1))
        return 0.0

    def load(self, paths: list[pathlib.Path]) -> pd.DataFrame:
        """Reads yearly JSON files into one table of actions.

        Args:
            paths: The JSON files, each a list of NSE action records.

        Returns:
            A table with columns symbol, ex_date, factor and dividend, one
            row per distinct action that changes a price or pays cash.

        Raises:
            None.
        """
        records = []
        for path in paths:
            records.extend(json.loads(path.read_text()))
        rows = []
        seen = set()
        for record in records:
            ex_text = record.get('exDate')
            if not ex_text or ex_text == '-':
                continue
            key = (record['symbol'], ex_text, record['subject'])
            if key in seen:
                continue
            seen.add(key)
            try:
                face_value = float(record.get('faceVal'))
            except TypeError, ValueError:
                face_value = float('nan')
            factor, dividend = self.parse_subject(record['subject'], face_value)
            if factor == 1.0 and dividend == 0.0:
                continue
            rows.append(
                {
                    'symbol': record['symbol'].strip(),
                    'ex_date': pd.to_datetime(ex_text, format='%d-%b-%Y'),
                    'factor': factor,
                    'dividend': dividend,
                }
            )
        return pd.DataFrame(
            rows, columns=['symbol', 'ex_date', 'factor', 'dividend']
        )
