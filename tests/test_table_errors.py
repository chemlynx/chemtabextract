"""Tests for Table error handling and boundary conditions.

Covers the InputError and TypeError paths raised by Table.__init__ and the
underlying from_any.create_table dispatcher, which are not exercised by the
happy-path integration tests.
"""

from pathlib import Path

import numpy as np
import pytest

from chemtabextract import Table
from chemtabextract.exceptions import InputError


class TestTableEmptyInput:
    """Table should raise InputError when given an all-empty input."""

    def test_all_empty_cells_raises_input_error(self) -> None:
        """Table with every cell empty should raise InputError on construction."""
        with pytest.raises(InputError):
            Table([["", ""], ["", ""]])

    def test_input_error_message_mentions_empty(self) -> None:
        """The InputError message should identify the table as empty."""
        with pytest.raises(InputError) as exc_info:
            Table([["", ""], ["", ""]])
        assert "empty" in exc_info.value.message.lower()

    def test_whitespace_only_cells_raises_input_error(self) -> None:
        """Cells containing only whitespace are treated as empty by empty_cells()."""
        with pytest.raises(InputError):
            Table([[" ", "  "], ["\t", "   "]])


class TestTableOneDimensionalInput:
    """Table should raise InputError when the raw array is 1-D.

    This path is reached when from_any.create_table returns a 1-D numpy array
    (e.g. an HTML page whose single-row table is parsed as a flat array).
    We monkeypatch create_table to inject the 1-D array without requiring a
    live HTML fixture.
    """

    def test_1d_array_raises_input_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A 1-D numpy array from create_table should raise InputError."""
        monkeypatch.setattr(
            "chemtabextract.table.table.from_any.create_table",
            lambda *a, **kw: np.array(["col1", "col2", "col3"], dtype="<U60"),
        )
        with pytest.raises(InputError):
            Table("dummy")

    def test_1d_error_message_mentions_row_or_column(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The InputError message should indicate a single-row/column problem."""
        monkeypatch.setattr(
            "chemtabextract.table.table.from_any.create_table",
            lambda *a, **kw: np.array(["col1", "col2"], dtype="<U60"),
        )
        with pytest.raises(InputError) as exc_info:
            Table("dummy")
        msg = exc_info.value.message.lower()
        assert "row" in msg or "column" in msg


class TestTableUnknownConfigKey:
    """Table should raise InputError for unrecognised keyword arguments."""

    def test_unknown_kwarg_raises_input_error(self) -> None:
        """Passing an unrecognised config keyword should raise InputError."""
        src = "./tests/data/table_example1.csv"
        with pytest.raises(InputError):
            Table(src, nonexistent_option=True)

    def test_error_message_names_bad_key(self) -> None:
        """The InputError message should include the offending keyword name."""
        src = "./tests/data/table_example1.csv"
        with pytest.raises(InputError) as exc_info:
            Table(src, definitely_not_a_real_key=42)
        assert "definitely_not_a_real_key" in exc_info.value.message


class TestCreateTableErrorPaths:
    """from_any.create_table should raise TypeError for invalid inputs."""

    def test_empty_list_raises_type_error(self) -> None:
        """An empty list input should raise TypeError before reaching the algorithm."""
        from chemtabextract.input.from_any import create_table

        with pytest.raises(TypeError):
            create_table([])

    def test_unrecognised_string_raises_type_error(self, tmp_path: Path) -> None:
        """A string that is not a URL, HTML file, or CSV file should raise TypeError."""
        from chemtabextract.input.from_any import create_table

        # Use a non-existent path with an unrecognised extension
        with pytest.raises(TypeError):
            create_table(str(tmp_path / "no_such_file.xyz"))

    def test_empty_list_via_table_raises_type_error(self) -> None:
        """Table([]) should propagate the TypeError from create_table."""
        with pytest.raises(TypeError):
            Table([])
