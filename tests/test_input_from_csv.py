"""
chemtabextract.tests.test_input_from_csv.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test table parsers.
Juraj Mavračić (jm2111@cam.ac.uk)
Ed Beard (ejb207@cam.ac.uk)
"""

import logging
from pathlib import Path

import numpy as np
import pytest

from chemtabextract import Table
from chemtabextract.input import from_csv

log = logging.getLogger(__name__)


def test_input_with_commas():
    path = Path(__file__).parent / "data" / "table_commas.csv"
    table = Table(path)

    table.print()
    assert table.raw_table[0][6] == "PCE (η, %)"
    assert table.raw_table[1][0] == "2H–MoS2 (hydrothermal, 200 °C)"
    assert table.raw_table[2][0] == "1T–MoS2 (hydrothermal, 180 °C)"


def test_input_with_double_quotes():
    path = Path(__file__).parent / "data" / "table_double_quotes.csv"
    table = Table(path)

    assert table.raw_table[1][0] == 'N719 "cell'
    assert table.raw_table[3][0] == 'Hy"brid cell'


def test_input_with_single_quotes():
    path = Path(__file__).parent / "data" / "table_single_quotes.csv"
    table = Table(path)

    assert table.raw_table[1][0] == "N719 'cell"
    assert table.raw_table[2][0] == "N74'9 cell"
    assert table.raw_table[3][2] == "13'.8"


def test_input_with_blank_lines():
    path = Path(__file__).parent / "data" / "table_empty_lines.csv"
    table = Table(path)

    assert table.raw_table[0][6] == "PCE (η, %)"
    assert table.raw_table[1][0] == "2H–MoS2 (hydrothermal, 200 °C)"
    assert table.raw_table[2][0] == "1T–MoS2 (hydrothermal, 180 °C)"


def test_table_with_broken_rows():
    path = Path(__file__).parent / "data" / "table_broken_row.csv"
    table = Table(path)

    assert len(table.category_table) == 10


# ---------------------------------------------------------------------------
# Dynamic dtype — Q7
# ---------------------------------------------------------------------------


class TestFromCsvDynamicDtype:
    """from_csv.read() computes dtype width from actual cell content (Q7).

    Before Q7 the dtype was hard-coded to ``<U60``, silently truncating any
    cell value longer than 60 characters.  After Q7 the dtype is derived from
    the maximum cell length so that no truncation can occur.
    """

    def test_cells_longer_than_60_chars_stored_in_full(self, tmp_path: Path) -> None:
        """A cell with 100 characters must survive the round-trip without truncation."""
        long_cell = "A" * 100  # exceeds the old <U60 limit
        csv_path = tmp_path / "long_cells.csv"
        csv_path.write_text(f"header\n{long_cell}\n", encoding="utf-8")

        result = from_csv.read(str(csv_path))

        assert result[1, 0] == long_cell

    def test_dtype_width_matches_longest_cell(self, tmp_path: Path) -> None:
        """The array dtype itemsize should be exactly wide enough for the longest cell."""
        long_cell = "B" * 75
        csv_path = tmp_path / "sized_cells.csv"
        csv_path.write_text(f"short,{long_cell}\nval,other\n", encoding="utf-8")

        result = from_csv.read(str(csv_path))

        # Each Unicode character occupies 4 bytes in a NumPy fixed-width dtype.
        assert result.dtype.itemsize == 75 * 4

    def test_truncation_warning_logged_for_cells_over_200_chars(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A WARNING-level log entry must be emitted when any cell exceeds 200 chars."""
        oversized_cell = "C" * 201
        csv_path = tmp_path / "oversized.csv"
        csv_path.write_text(f"header\n{oversized_cell}\n", encoding="utf-8")

        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_csv"):
            from_csv.read(str(csv_path))

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("201" in msg for msg in warning_messages)

    def test_no_warning_for_cells_at_or_below_200_chars(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """No warning should be logged when all cells are at or below 200 characters."""
        cell_200 = "D" * 200  # exactly at the threshold — should not warn
        csv_path = tmp_path / "threshold.csv"
        csv_path.write_text(f"header\n{cell_200}\n", encoding="utf-8")

        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_csv"):
            from_csv.read(str(csv_path))

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert not warning_messages

    def test_short_cells_produce_unicode_dtype(self, tmp_path: Path) -> None:
        """A normal CSV with short cells should still produce a Unicode array dtype."""
        csv_path = tmp_path / "normal.csv"
        csv_path.write_text("A,B\n1,2\n", encoding="utf-8")

        result = from_csv.read(str(csv_path))

        assert np.issubdtype(result.dtype, np.str_)
