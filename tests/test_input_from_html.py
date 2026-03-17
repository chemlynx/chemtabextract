"""Tests for chemtabextract.input.from_html.read_file.

Covers the context-manager open (resource-safety fix) and the
IndexError → InputError conversion for out-of-range table_number values.
Both paths were modified in commit f2edc1f; from_html had only 10% branch
coverage before this file.

HTML fixtures are written inline via tmp_path to keep the test data
self-documenting and avoid adding files to tests/data/.
"""

from pathlib import Path

import numpy as np
import pytest

from chemtabextract.exceptions import InputError
from chemtabextract.input.from_html import read_file

# ---------------------------------------------------------------------------
# Inline HTML content used across multiple tests
# ---------------------------------------------------------------------------

_SINGLE_TABLE_HTML = """\
<html><body>
<table>
  <tr><th>Compound</th><th>Yield (%)</th></tr>
  <tr><td>Aspirin</td><td>85</td></tr>
  <tr><td>Caffeine</td><td>72</td></tr>
</table>
</body></html>
"""

_TWO_TABLE_HTML = """\
<html><body>
<table>
  <tr><th>T1C1</th><th>T1C2</th></tr>
  <tr><td>a</td><td>b</td></tr>
</table>
<table>
  <tr><th>T2C1</th><th>T2C2</th></tr>
  <tr><td>c</td><td>d</td></tr>
</table>
</body></html>
"""


@pytest.fixture()
def single_table_html(tmp_path: Path) -> Path:
    """One-table HTML file at a temporary path."""
    p = tmp_path / "single.html"
    p.write_text(_SINGLE_TABLE_HTML, encoding="utf-8")
    return p


@pytest.fixture()
def two_table_html(tmp_path: Path) -> Path:
    """Two-table HTML file at a temporary path."""
    p = tmp_path / "two_tables.html"
    p.write_text(_TWO_TABLE_HTML, encoding="utf-8")
    return p


class TestReadFileReturnType:
    """read_file should always return a correctly typed numpy array."""

    def test_returns_numpy_ndarray(self, single_table_html: Path) -> None:
        """read_file should return an ndarray, not a list or other type."""
        result = read_file(str(single_table_html))
        assert isinstance(result, np.ndarray)

    def test_array_dtype_is_u60(self, single_table_html: Path) -> None:
        """Array dtype should be '<U60', consistent with the CSV and list input paths."""
        result = read_file(str(single_table_html))
        assert result.dtype == np.dtype("<U60")


class TestReadFileSingleTable:
    """read_file correctly parses a file containing exactly one table."""

    def test_shape_matches_html_table_dimensions(self, single_table_html: Path) -> None:
        """A 3-row × 2-col HTML table should produce a (3, 2) array."""
        result = read_file(str(single_table_html))
        assert result.shape == (3, 2)

    def test_header_row_content(self, single_table_html: Path) -> None:
        """First row should contain the <th> cell text values."""
        result = read_file(str(single_table_html))
        assert result[0, 0] == "Compound"
        assert result[0, 1] == "Yield (%)"

    def test_data_row_content(self, single_table_html: Path) -> None:
        """Subsequent rows should contain the <td> cell text values."""
        result = read_file(str(single_table_html))
        assert result[1, 0] == "Aspirin"
        assert result[1, 1] == "85"
        assert result[2, 0] == "Caffeine"
        assert result[2, 1] == "72"


class TestReadFileTableNumber:
    """read_file respects the table_number parameter."""

    def test_table_number_1_returns_first_table(self, two_table_html: Path) -> None:
        """table_number=1 should return the first <table> element."""
        result = read_file(str(two_table_html), table_number=1)
        assert result[0, 0] == "T1C1"
        assert result[0, 1] == "T1C2"

    def test_table_number_2_returns_second_table(self, two_table_html: Path) -> None:
        """table_number=2 should return the second <table> element."""
        result = read_file(str(two_table_html), table_number=2)
        assert result[0, 0] == "T2C1"
        assert result[0, 1] == "T2C2"

    def test_out_of_range_table_number_raises_input_error(self, single_table_html: Path) -> None:
        """Requesting table_number=2 from a one-table file should raise InputError.

        This exercises the IndexError → InputError conversion introduced in
        commit f2edc1f to replace the previous bare IndexError propagation.
        """
        with pytest.raises(InputError):
            read_file(str(single_table_html), table_number=2)

    def test_out_of_range_message_names_table_number_param(self, single_table_html: Path) -> None:
        """The InputError message should reference 'table_number' by name."""
        with pytest.raises(InputError) as exc_info:
            read_file(str(single_table_html), table_number=2)
        assert "table_number" in exc_info.value.message

    def test_out_of_range_message_includes_requested_value(self, single_table_html: Path) -> None:
        """The InputError message should include the actual bad value."""
        with pytest.raises(InputError) as exc_info:
            read_file(str(single_table_html), table_number=99)
        assert "99" in exc_info.value.message

    def test_input_error_is_catchable_as_base_exception(self, single_table_html: Path) -> None:
        """The raised InputError should be catchable as a plain Exception."""
        with pytest.raises(Exception):
            read_file(str(single_table_html), table_number=2)
