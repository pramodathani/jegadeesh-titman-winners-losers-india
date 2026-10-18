"""Tests for reading corporate actions."""

import json
import math
import pathlib

import pytest

from jegadeesh_titman_india.data.corporate_actions import CorporateActionTable

SUB_DIVISION = 'Face Value Split (Sub-Division) - From Rs 10/- Per Share To Rs 2/- Per Share'


class TestCorporateActionTable:
    """Checks on the wording of splits, bonuses and dividends."""

    @pytest.mark.parametrize(
        ('subject', 'face_value', 'factor', 'dividend'),
        [
            ('Bonus 1:1', 10.0, 2.0, 0.0),
            ('Bonus 3:2', 2.0, 2.5, 0.0),
            ('Fv Split Rs.10 To Re.1', 10.0, 10.0, 0.0),
            (SUB_DIVISION, 10.0, 5.0, 0.0),
            ('Face Value Consolidation From Rs 1 To Rs 10', 1.0, 0.1, 0.0),
            ('Interim Dividend - Rs 2.5 Per Share', 1.0, 1.0, 2.5),
            ('AGM/Dividend-250%', 10.0, 1.0, 25.0),
            ('AGM/Div-Re.1 Per Sh', 1.0, 1.0, 1.0),
            ('Annual General Meeting', 10.0, 1.0, 0.0),
            ('Interest Payment', 10.0, 1.0, 0.0),
            (
                'Bonus 22:1 And Face Value Split From Rs.10/- To Re.1/-',
                1.0,
                230.0,
                0.0,
            ),
        ],
    )
    def test_parse_subject(
        self,
        subject: str,
        face_value: float,
        factor: float,
        dividend: float,
    ) -> None:
        """Checks that wording gives the right factor and dividend.

        Args:
            subject: The action's wording.
            face_value: The face value in rupees.
            factor: The expected price factor.
            dividend: The expected dividend.

        Returns:
            None.

        Raises:
            AssertionError: When the result differs.
        """
        result = CorporateActionTable().parse_subject(subject, face_value)
        assert math.isclose(result[0], factor)
        assert math.isclose(result[1], dividend)

    def test_load_drops_duplicates_and_no_ops(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Checks that a repeated action appears once and AGMs are dropped.

        Args:
            tmp_path: A temporary folder.

        Returns:
            None.

        Raises:
            AssertionError: When the table is wrong.
        """
        record = {
            'symbol': 'AAA',
            'exDate': '04-Jan-2010',
            'subject': 'Bonus 1:1',
            'faceVal': '10',
        }
        agm = dict(record, subject='Annual General Meeting')
        missing = dict(record, exDate='-')
        first = tmp_path / '2010.json'
        second = tmp_path / '2011.json'
        first.write_text(json.dumps([record, agm, missing]))
        second.write_text(json.dumps([record]))
        table = CorporateActionTable().load([first, second])
        assert len(table) == 1
        assert table['factor'].iloc[0] == 2.0
