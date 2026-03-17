"""Tests for chemtabextract.output.to_pandas — print_category_table and helpers.

Covers print_category_table() which was listed in IMPROVEMENTS.md TC2 as
entirely untested.  The function iterates over DataFrame values, calls
find_multiindex_level() for each cell, and prints a formatted row to stdout.

Tests use capsys to capture printed output rather than mocking print().
"""

import pandas as pd
import pytest

from chemtabextract.output.to_pandas import build_category_table, print_category_table

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_df() -> pd.DataFrame:
    """A minimal 2×2 DataFrame with MultiIndex rows and columns.

    Structure::

        columns:  ("ColA",) | ("ColB",)
        rows:
          ("RowX",)  1        2
          ("RowY",)  3        4

    This is the simplest structure accepted by print_category_table() that
    exercises both row and column MultiIndex paths in find_multiindex_level().
    """
    index = pd.MultiIndex.from_tuples([("RowX",), ("RowY",)], names=["row"])
    columns = pd.MultiIndex.from_tuples([("ColA",), ("ColB",)], names=["col"])
    return pd.DataFrame([[1, 2], [3, 4]], index=index, columns=columns)


# ---------------------------------------------------------------------------
# TestPrintCategoryTable — TC2
# ---------------------------------------------------------------------------


class TestPrintCategoryTable:
    """Tests for print_category_table()."""

    def test_print_category_table_writes_to_stdout(
        self, simple_df: pd.DataFrame, capsys: pytest.CaptureFixture
    ) -> None:
        """Should write at least one line to stdout for a non-empty DataFrame."""
        print_category_table(simple_df)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_category_table_header_line_present(
        self, simple_df: pd.DataFrame, capsys: pytest.CaptureFixture
    ) -> None:
        """The output should contain the fixed column-header line."""
        print_category_table(simple_df)
        captured = capsys.readouterr()
        # The function always prints a header: "Cell_ID  Data  Row Categories  ..."
        assert "Cell_ID" in captured.out
        assert "Data" in captured.out

    def test_print_category_table_contains_data_values(
        self, simple_df: pd.DataFrame, capsys: pytest.CaptureFixture
    ) -> None:
        """Should print each cell's data value."""
        print_category_table(simple_df)
        captured = capsys.readouterr()
        # Values 1, 2, 3, 4 should all appear in the output.
        for val in ("1", "2", "3", "4"):
            assert val in captured.out

    def test_print_category_table_does_not_raise_for_empty_dataframe(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Should not raise for an empty DataFrame — just prints the header line."""
        empty_df = pd.DataFrame()
        print_category_table(empty_df)  # must not raise
        captured = capsys.readouterr()
        # Header line still expected even for an empty frame.
        assert "Cell_ID" in captured.out

    def test_print_category_table_one_line_per_cell(
        self, simple_df: pd.DataFrame, capsys: pytest.CaptureFixture
    ) -> None:
        """Output should have one data line per cell plus the header line.

        The fixture is 2×2 = 4 cells, so expect 5 lines total (header + 4).
        """
        print_category_table(simple_df)
        captured = capsys.readouterr()
        # Strip trailing blank line; count non-empty lines.
        lines = [ln for ln in captured.out.splitlines() if ln.strip()]
        assert len(lines) == 5  # 1 header + 4 data cells


# ---------------------------------------------------------------------------
# build_category_table — basic sanity (used by print_category_table)
# ---------------------------------------------------------------------------


class TestBuildCategoryTable:
    """Sanity tests for build_category_table(), which backs the print function."""

    def test_build_returns_list(self, simple_df: pd.DataFrame) -> None:
        """build_category_table() should return a list."""
        result = build_category_table(simple_df)
        assert isinstance(result, list)

    def test_build_has_one_entry_per_cell(self, simple_df: pd.DataFrame) -> None:
        """Number of entries should equal rows × columns."""
        result = build_category_table(simple_df)
        assert len(result) == 4  # 2 rows × 2 cols

    def test_build_entry_structure(self, simple_df: pd.DataFrame) -> None:
        """Each entry should be [data_value, row_categories, col_categories]."""
        result = build_category_table(simple_df)
        for entry in result:
            assert len(entry) == 3
            data, row_cats, col_cats = entry
            assert isinstance(row_cats, list)
            assert isinstance(col_cats, list)
