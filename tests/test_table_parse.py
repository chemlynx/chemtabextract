"""Tests for chemtabextract.table.parse.CellParser.

Covers the 1-D input guard added by Q5 (ValueError on ndim != 2) and the
2-D happy path of cut(), both of which were entirely uncovered before this
suite.

CellParser.cut() semantics:
  - Uses parse() internally to find cells matching the pattern.
  - method="match"  → pattern must match at the START of the cell string.
  - method="search" → pattern can match anywhere in the string.
  - For each matching cell, yields (row, col, residual) where residual is the
    entire cell value with ALL occurrences of the pattern globally removed
    (prog.sub("", cell)).
  - Cells that do not match are skipped entirely — they produce no output.
"""

import types

import numpy as np
import pytest

from chemtabextract.table.parse import CellParser  # noqa: E402

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def digit_parser() -> CellParser:
    """CellParser whose pattern matches one or more consecutive digits."""
    return CellParser(r"\d+")


@pytest.fixture()
def two_by_two_table() -> np.ndarray:
    """2-D table with two digit-prefixed cells and two non-matching cells.

    Layout::

        [["123abc",  "xyz"     ],
         ["no_match","456"     ]]

    With pattern ``r"\\d+"`` and ``method="match"`` (default):

    - ``(0, 0)  "123abc"``  → matches (starts with digits); residual ``"abc"``
    - ``(0, 1)  "xyz"``     → no match (starts with a letter); skipped
    - ``(1, 0)  "no_match"``→ no match (starts with a letter); skipped
    - ``(1, 1)  "456"``     → matches (starts with digits); residual ``""``
    """
    return np.array(
        [["123abc", "xyz"], ["no_match", "456"]],
        dtype="<U10",
    )


# ---------------------------------------------------------------------------
# Guard tests — 1-D input must raise ValueError
# ---------------------------------------------------------------------------


class TestCellParserCutGuard:
    """cut() must raise ValueError when passed a non-2-D array."""

    def test_cut_raises_value_error_for_1d_array(self, digit_parser: CellParser) -> None:
        """Should raise ValueError immediately when the input array has ndim=1."""
        table_1d = np.array(["123abc", "xyz", "456"])
        with pytest.raises(ValueError):
            # cut() is a generator; list() forces evaluation to trigger the guard.
            list(digit_parser.cut(table_1d))

    def test_cut_error_message_includes_actual_ndim(self, digit_parser: CellParser) -> None:
        """ValueError message should state the actual ndim of the rejected array."""
        table_1d = np.array(["abc", "def"])
        with pytest.raises(ValueError, match="ndim=1"):
            list(digit_parser.cut(table_1d))

    def test_cut_error_message_mentions_2d_requirement(self, digit_parser: CellParser) -> None:
        """ValueError message should communicate that a 2-D array is required."""
        table_1d = np.array(["abc"])
        with pytest.raises(ValueError, match="2-D"):
            list(digit_parser.cut(table_1d))


# ---------------------------------------------------------------------------
# Happy-path tests — 2-D input
# ---------------------------------------------------------------------------


class TestCellParserCut2D:
    """cut() happy path with a 2-D array and the default method='match'.

    Uses the ``two_by_two_table`` fixture defined at module level.
    """

    def test_cut_returns_generator(
        self,
        digit_parser: CellParser,
        two_by_two_table: np.ndarray,
    ) -> None:
        """cut() should be lazy — it must return a generator, not a list."""
        result = digit_parser.cut(two_by_two_table)
        assert isinstance(result, types.GeneratorType)

    def test_cut_yields_only_matching_cells(
        self,
        digit_parser: CellParser,
        two_by_two_table: np.ndarray,
    ) -> None:
        """cut() should yield exactly one result per matching cell."""
        results = list(digit_parser.cut(two_by_two_table))
        assert len(results) == 2

    def test_cut_yields_correct_indices_for_matching_cells(
        self,
        digit_parser: CellParser,
        two_by_two_table: np.ndarray,
    ) -> None:
        """Yielded (row, col) pairs must identify the matched cells."""
        results = list(digit_parser.cut(two_by_two_table))
        indices = {(r, c) for r, c, _ in results}
        assert (0, 0) in indices  # "123abc" starts with digits
        assert (1, 1) in indices  # "456"    starts with digits

    def test_cut_non_matching_cells_absent_from_output(
        self,
        digit_parser: CellParser,
        two_by_two_table: np.ndarray,
    ) -> None:
        """Cells that do not match the pattern should produce no output entry."""
        results = list(digit_parser.cut(two_by_two_table))
        indices = {(r, c) for r, c, _ in results}
        assert (0, 1) not in indices  # "xyz"      — does not start with digits
        assert (1, 0) not in indices  # "no_match" — does not start with digits

    @pytest.mark.parametrize(
        ("cell_value", "expected_residual"),
        [
            ("123abc", "abc"),  # leading digits removed; trailing letters remain
            ("456", ""),  # cell is entirely digits; nothing remains
        ],
        ids=["partial-match-leading-digits", "full-match-all-digits"],
    )
    def test_cut_residual_has_matched_pattern_removed(
        self,
        cell_value: str,
        expected_residual: str,
    ) -> None:
        """Residual string should be the cell value with the pattern globally removed."""
        parser = CellParser(r"\d+")
        table = np.array([[cell_value, "skip_me"]], dtype=f"<U{max(len(cell_value), 7)}")
        results = list(parser.cut(table))
        assert len(results) == 1
        assert results[0][2] == expected_residual

    def test_cut_result_tuple_has_three_elements(
        self,
        digit_parser: CellParser,
        two_by_two_table: np.ndarray,
    ) -> None:
        """Each yielded item must be a 3-tuple of (row, col, residual_string)."""
        results = list(digit_parser.cut(two_by_two_table))
        for item in results:
            assert len(item) == 3
            row, col, residual = item
            assert isinstance(row, int | np.integer)
            assert isinstance(col, int | np.integer)
            assert isinstance(residual, str)
