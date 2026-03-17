"""Tests for chemtabextract.table.parse — CellParser and StringParser.

Covers:
- CellParser.cut(): 1-D input guard (Q5), 2-D happy path
- CellParser.replace(): pattern substitution on matching cells (TC2)
- StringParser.cut(): residual-string extraction on a single string (TC2)

CellParser.cut() semantics:
  - Uses parse() internally to find cells matching the pattern.
  - method="match"  → pattern must match at the START of the cell string.
  - method="search" → pattern can match anywhere in the string.
  - For each matching cell, yields (row, col, residual) where residual is the
    entire cell value with ALL occurrences of the pattern globally removed
    (prog.sub("", cell)).
  - Cells that do not match are skipped entirely — they produce no output.

CellParser.replace() semantics:
  - Same pattern-matching logic as cut().
  - For each matching cell, yields (row, col, replaced_string) where
    replaced_string has the matched portion substituted with repl.
  - Non-matching cells are skipped.

StringParser.cut() semantics:
  - Operates on a single string (not a 2-D array).
  - Returns the input string with all occurrences of the pattern globally
    removed (prog.sub("", string)).
"""

import types

import numpy as np
import pytest

from chemtabextract.table.parse import CellParser, StringParser  # noqa: E402

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


# ---------------------------------------------------------------------------
# CellParser.replace() tests — TC2
# ---------------------------------------------------------------------------


@pytest.fixture()
def mixed_array() -> np.ndarray:
    """2-D table with digit-prefixed cells and non-matching cells.

    Layout::

        [["42 apples", "oranges"],
         ["no_digits", "7 bananas"]]

    With pattern ``r"\\d+"`` and ``method="match"`` (default):

    - ``(0, 0)  "42 apples"``  → matches; replace("NUM") → ``"NUM apples"``
    - ``(0, 1)  "oranges"``    → no match; skipped
    - ``(1, 0)  "no_digits"``  → no match; skipped
    - ``(1, 1)  "7 bananas"``  → matches; replace("NUM") → ``"NUM bananas"``
    """
    return np.array(
        [["42 apples", "oranges"], ["no_digits", "7 bananas"]],
        dtype="<U20",
    )


class TestCellParserReplace:
    """CellParser.replace() substitutes the matched pattern in each matching cell."""

    def test_replace_returns_generator(self, mixed_array: np.ndarray) -> None:
        """replace() should be lazy — it must return a generator, not a list."""
        parser = CellParser(r"\d+")
        result = parser.replace(mixed_array, "NUM")
        assert isinstance(result, types.GeneratorType)

    def test_replace_yields_only_matching_cells(self, mixed_array: np.ndarray) -> None:
        """replace() should yield exactly one result per matching cell."""
        results = list(CellParser(r"\d+").replace(mixed_array, "NUM"))
        assert len(results) == 2

    def test_replace_substitutes_pattern_in_matching_cells(self, mixed_array: np.ndarray) -> None:
        """Matching cells should have the pattern replaced by the replacement string."""
        results = {(r, c): s for r, c, s in CellParser(r"\d+").replace(mixed_array, "NUM")}
        assert results[(0, 0)] == "NUM apples"
        assert results[(1, 1)] == "NUM bananas"

    def test_replace_does_not_modify_non_matching_cells(self, mixed_array: np.ndarray) -> None:
        """Non-matching cells (0,1) and (1,0) should not appear in the output."""
        results = {(r, c) for r, c, _ in CellParser(r"\d+").replace(mixed_array, "NUM")}
        assert (0, 1) not in results  # "oranges" — no digits
        assert (1, 0) not in results  # "no_digits" — starts with letter

    def test_replace_result_tuple_has_three_elements(self, mixed_array: np.ndarray) -> None:
        """Each yielded item must be a 3-tuple of (row, col, replaced_string)."""
        for item in CellParser(r"\d+").replace(mixed_array, "NUM"):
            assert len(item) == 3
            row, col, replaced = item
            assert isinstance(row, int | np.integer)
            assert isinstance(col, int | np.integer)
            assert isinstance(replaced, str)

    def test_replace_raises_on_1d_array(self) -> None:
        """Should raise an exception when passed a 1-D array.

        Unlike cut(), replace() does not have an explicit ndim guard; it raises
        IndexError when it tries to index the 1-D array with a 2-tuple.  The
        important property is that it does not silently return wrong results.
        """
        table_1d = np.array(["42 apples", "oranges"])
        parser = CellParser(r"\d+")
        with pytest.raises((ValueError, AssertionError, IndexError)):
            list(parser.replace(table_1d, "NUM"))


# ---------------------------------------------------------------------------
# StringParser.cut() tests — TC2
# ---------------------------------------------------------------------------


class TestStringParserCut:
    """StringParser.cut() removes all occurrences of the pattern from a string."""

    def test_cut_returns_string(self) -> None:
        """cut() should return a str object."""
        result = StringParser(r"\d+").cut("abc123def")
        assert isinstance(result, str)

    def test_cut_removes_matched_portion(self) -> None:
        """Should globally remove the pattern from the input string."""
        result = StringParser(r"\d+").cut("abc123def456")
        assert result == "abcdef"

    def test_cut_returns_expected_residual(self) -> None:
        """Residual should have the matched token removed but surrounding text intact."""
        # Pattern captures 'key=value'; cut() removes the whole match.
        result = StringParser(r"\w+=\w+").cut("key=value remainder")
        assert "key=value" not in result
        assert "remainder" in result

    def test_cut_returns_full_string_when_no_match(self) -> None:
        """When the pattern does not match, the original string should be returned unchanged."""
        original = "no match here"
        result = StringParser(r"\d+").cut(original)
        assert result == original

    def test_cut_returns_empty_string_for_full_match(self) -> None:
        """When the entire string matches, cut() should return an empty string."""
        result = StringParser(r"\d+").cut("12345")
        assert result == ""
