"""Tests for chemtabextract.input.from_html — read_file, makearray, read_url, configure_selenium.

Covers:
- read_file: context-manager open and IndexError → InputError conversion (TC1 pre-existing)
- makearray: colspan/rowspan corner-cell fill (Q6) and dynamic dtype (Q7)
- read_url: happy path via requests mock, error paths, and Selenium fallback (TC1 new)
- configure_selenium: Firefox driver construction and unknown-browser fallback (TC1 new)

All read_url and configure_selenium tests use unittest.mock.patch to avoid any
real network calls or browser processes.  The patch target is always the
fully-qualified name inside the from_html module, e.g.
``chemtabextract.input.from_html.requests.get``.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import requests
from bs4 import BeautifulSoup

from chemtabextract.exceptions import InputError
from chemtabextract.input.from_html import configure_selenium, makearray, read_file, read_url

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

    def test_array_dtype_is_unicode_string(self, single_table_html: Path) -> None:
        """Array dtype should be a fixed-width Unicode string dtype."""
        result = read_file(str(single_table_html))
        assert np.issubdtype(result.dtype, np.str_)


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


# ---------------------------------------------------------------------------
# Helpers — build a BeautifulSoup <table> element from an HTML string
# ---------------------------------------------------------------------------


def _parse_table(html: str):
    """Return the first <table> Tag from an HTML fragment."""
    return BeautifulSoup(html, "lxml").find("table")


# ---------------------------------------------------------------------------
# makearray — corner cell fill (Q6)
# ---------------------------------------------------------------------------


class TestMakearrayCornerCellFill:
    """makearray() must fill the intersection cells when colspan and rowspan both present.

    Before Q6 the row-span cells and column-span cells were filled
    independently, but the intersection corner cells were left empty.
    After Q6 a nested ``product()`` loop fills every ``(row+r, col+c)``
    combination.

    **Known limitation (Action 0 in qa_dev_actions_improvements-backlog-sweep.md):**
    Two pre-existing defects constrain which table structures work correctly:

    1. ``n_cols`` is computed by counting visible ``<td>/<th>`` tags per row
       without accounting for ``colspan``.  Any table where the widest row
       contains a combined-span cell will have an undersized ``n_cols`` and
       raise ``IndexError``.
    2. ``skip_index`` is only updated for the leftmost column of a combined
       cell.  When the combined cell is at col 0, the next row's cells land on
       the corner-filled position and overwrite it.

    The working test below uses a header row to establish the correct ``n_cols``
    and places the combined cell at col 1 (not col 0) so neither defect applies.
    The ``xfail`` test documents the crash that occurs with the most natural
    table structure (no header row, combined cell at col 0).
    """

    def test_combined_rowspan_colspan_fills_corner_cell(self) -> None:
        """A cell with rowspan=2 and colspan=2 must fill the intersection corner.

        This test uses a valid table structure for the current algorithm:
        a header row establishes ``n_cols = 3`` and the combined cell is at
        col 1 (not col 0) so skip_index propagates correctly.

        HTML structure (combined cell B at row 1, col 1)::

            H1   H2   H3
            A    B    B     ← B at col 1: colspan fills (1,2); rowspan fills (2,1)
            C    B    B     ← corner (2,2) filled by Q6; C at (2,0), not overwritten

        Before Q6: ``result[2, 2]`` was ``""`` (empty — corner not filled).
        After Q6:  ``result[2, 2]`` is ``"B"`` (corner fill from product loop).
        """
        html = """
        <table>
          <tr><td>H1</td><td>H2</td><td>H3</td></tr>
          <tr><td>A</td><td rowspan="2" colspan="2">B</td></tr>
          <tr><td>C</td></tr>
        </table>
        """
        result = makearray(_parse_table(html))

        assert result.shape == (3, 3)
        # Header row — unaffected.
        assert result[0, 0] == "H1"
        assert result[0, 1] == "H2"
        assert result[0, 2] == "H3"
        # Row 1: A at col 0; B fills cols 1 and 2 (colspan).
        assert result[1, 0] == "A"
        assert result[1, 1] == "B"  # original cell
        assert result[1, 2] == "B"  # colspan fill (was correct before Q6)
        # Row 2: C at col 0; B propagated by rowspan and corner fill.
        assert result[2, 0] == "C"
        assert result[2, 1] == "B"  # rowspan fill (was correct before Q6)
        assert result[2, 2] == "B"  # corner fill  ← the Q6 fix

    def test_combined_rowspan_colspan_fills_2x2_block(self) -> None:
        """A combined rowspan=2/colspan=2 cell fills a full 2×2 block correctly.

        Action 0 (P0) fixed two defects in makearray():
        1. ``n_cols`` now sums ``colspan`` values rather than counting tags, so the
           array is correctly sized at 3 columns.
        2. ``skip_index`` is now updated for every column a combined cell spans, so
           the row-2 cell ``C`` lands at ``(1, 2)`` rather than overwriting corner
           fill at ``(1, 1)``.

        Expected layout after the fix::

            A   A   B     ← A at (0,0); colspan fills (0,1); B at (0,2)
            A   A   C     ← rowspan fills (1,0) and (1,1); C at (1,2)
        """
        html = """
        <table>
          <tr><td rowspan="2" colspan="2">A</td><td>B</td></tr>
          <tr><td>C</td></tr>
        </table>
        """
        result = makearray(_parse_table(html))

        assert result.shape == (2, 3)
        assert result[0, 0] == "A"  # original cell
        assert result[0, 1] == "A"  # colspan fill
        assert result[0, 2] == "B"
        assert result[1, 0] == "A"  # rowspan fill
        assert result[1, 1] == "A"  # corner fill (rowspan + colspan intersection)
        assert result[1, 2] == "C"

    def test_rowspan_only_does_not_affect_adjacent_columns(self) -> None:
        """A cell with only rowspan (no colspan) should not bleed into other columns."""
        html = """
        <table>
          <tr><td rowspan="2">A</td><td>B</td></tr>
          <tr><td>C</td></tr>
        </table>
        """
        result = makearray(_parse_table(html))

        assert result[0, 0] == "A"
        assert result[1, 0] == "A"  # rowspan fill
        assert result[0, 1] == "B"
        assert result[1, 1] == "C"  # must not be "A"


# ---------------------------------------------------------------------------
# makearray — dynamic dtype (Q7)
# ---------------------------------------------------------------------------


class TestMakearrayDynamicDtype:
    """makearray() computes dtype width from actual cell content (Q7).

    Before Q7 the dtype was hard-coded to ``<U60``, silently truncating any
    cell value longer than 60 characters.
    """

    def test_cells_longer_than_60_chars_stored_in_full(self) -> None:
        """A cell with 100 characters must not be truncated."""
        long_cell = "X" * 100  # exceeds the old <U60 limit
        html = f"<table><tr><td>{long_cell}</td><td>short</td></tr></table>"
        result = makearray(_parse_table(html))
        assert result[0, 0] == long_cell

    def test_dtype_is_unicode(self) -> None:
        """The returned array must always have a Unicode string dtype."""
        html = "<table><tr><td>hello</td><td>world</td></tr></table>"
        result = makearray(_parse_table(html))
        assert np.issubdtype(result.dtype, np.str_)

    def test_truncation_warning_logged_for_cells_over_200_chars(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A WARNING must be emitted when any cell in the HTML table exceeds 200 chars."""
        oversized_cell = "Y" * 201
        html = f"<table><tr><td>{oversized_cell}</td><td>short</td></tr></table>"

        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_html"):
            makearray(_parse_table(html))

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("201" in msg for msg in warning_messages)

    def test_no_warning_for_cells_at_or_below_200_chars(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """No warning should be logged when all cells are 200 characters or fewer."""
        cell_200 = "Z" * 200  # exactly at the threshold
        html = f"<table><tr><td>{cell_200}</td><td>short</td></tr></table>"

        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_html"):
            makearray(_parse_table(html))

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert not warning_messages


# ---------------------------------------------------------------------------
# Shared HTML for read_url mock tests
# ---------------------------------------------------------------------------

# A minimal 2×3 HTML page (one table, one colspan cell) used to build mock
# responses for the read_url tests.  The table shape is 2 rows × 3 logical
# columns; the <colspan="2"> cell in row 1 makes it exercise makearray's
# spanning logic as well.
_READ_URL_HTML = """\
<html><body>
<table>
  <tr><td>H1</td><td>H2</td><td>H3</td></tr>
  <tr><td colspan="2">A</td><td>B</td></tr>
</table>
</body></html>
"""


def _mock_requests_response(html: str = _READ_URL_HTML) -> MagicMock:
    """Build a MagicMock that looks like a successful requests.Response."""
    resp = MagicMock()
    resp.text = html
    return resp


# ---------------------------------------------------------------------------
# TestReadUrl — mock-based coverage of read_url() (TC1)
# ---------------------------------------------------------------------------


class TestReadUrl:
    """Tests for read_url() using patched network dependencies.

    All HTTP calls are intercepted with unittest.mock.patch so no real network
    activity occurs.  The patch target is always the fully-qualified import
    inside from_html, e.g. ``chemtabextract.input.from_html.requests.get``.
    """

    def test_read_url_requests_path_returns_array(self) -> None:
        """Should return a numpy array when requests.get succeeds.

        Patches requests.get to return a mock response containing a 2×3 HTML
        table.  The patched path exercises the requests branch of read_url()
        without any network activity.
        """
        with patch(
            "chemtabextract.input.from_html.requests.get",
            return_value=_mock_requests_response(),
        ):
            result = read_url("http://example.com")

        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 3)

    def test_read_url_raises_type_error_for_non_integer_table_number(self) -> None:
        """Should raise TypeError when table_number is not an int."""
        with pytest.raises(TypeError):
            read_url("http://example.com", table_number="1")  # type: ignore[arg-type]

    def test_read_url_raises_input_error_for_out_of_range_table_number(self) -> None:
        """Should raise InputError when table_number exceeds the number of tables.

        Patches requests.get to return a page with exactly one table; requesting
        table_number=99 should raise InputError.
        """
        with (
            patch(
                "chemtabextract.input.from_html.requests.get",
                return_value=_mock_requests_response(),
            ),
            pytest.raises(InputError),
        ):
            read_url("http://example.com", table_number=99)

    def test_read_url_selenium_fallback_when_requests_fails(self) -> None:
        """Should fall back to Selenium and return an array when requests raises ConnectionError.

        Patches:
        - requests.get → raises ConnectionError
        - configure_selenium → returns a mock driver whose .page_source is
          a valid HTML page

        This exercises the ``except requests.exceptions.RequestException`` branch.
        """
        mock_driver = MagicMock()
        mock_driver.page_source = _READ_URL_HTML

        with (
            patch(
                "chemtabextract.input.from_html.requests.get",
                side_effect=requests.exceptions.ConnectionError("mock network failure"),
            ),
            patch(
                "chemtabextract.input.from_html._SELENIUM_AVAILABLE",
                True,
            ),
            patch(
                "chemtabextract.input.from_html.configure_selenium",
                return_value=mock_driver,
            ),
        ):
            result = read_url("http://example.com")

        assert isinstance(result, np.ndarray)

    def test_read_url_raises_input_error_when_selenium_unavailable(self) -> None:
        """Should raise InputError (mentioning web extra) when requests fails and Selenium absent.

        Patches requests.get to raise ConnectionError and _SELENIUM_AVAILABLE to
        False, simulating the environment where the optional web extra is not installed.
        """
        with (
            patch(
                "chemtabextract.input.from_html.requests.get",
                side_effect=requests.exceptions.ConnectionError("mock network failure"),
            ),
            patch(
                "chemtabextract.input.from_html._SELENIUM_AVAILABLE",
                False,
            ),
            pytest.raises(InputError) as exc_info,
        ):
            read_url("http://example.com")

        assert "web" in exc_info.value.message.lower()

    def test_read_url_first_table_returned_by_default(self) -> None:
        """Default table_number=1 should return the first table on the page."""
        two_table_page = """\
<html><body>
<table><tr><td>FIRST</td></tr></table>
<table><tr><td>SECOND</td></tr></table>
</body></html>
"""
        with patch(
            "chemtabextract.input.from_html.requests.get",
            return_value=_mock_requests_response(two_table_page),
        ):
            result = read_url("http://example.com")

        assert result[0, 0] == "FIRST"


# ---------------------------------------------------------------------------
# TestConfigureSelenium — mock-based coverage of configure_selenium() (TC1)
# ---------------------------------------------------------------------------


class TestConfigureSelenium:
    """Tests for configure_selenium() using patched Selenium dependencies.

    configure_selenium() is only reachable in production when the optional
    ``[web]`` extra is installed.  Here we patch the webdriver at module level
    to avoid any real browser dependency.
    """

    def test_configure_selenium_returns_firefox_driver(self) -> None:
        """Should call webdriver.Firefox once and return its result.

        Because the optional selenium extra may not be installed, ``webdriver``
        and ``FirefoxOptions`` may not exist in the module namespace.  We use
        ``create=True`` to inject mock replacements regardless, then verify
        that ``webdriver.Firefox`` is called exactly once.
        """
        fake_driver = MagicMock()
        mock_webdriver = MagicMock()
        mock_webdriver.Firefox.return_value = fake_driver

        with (
            patch(
                "chemtabextract.input.from_html.webdriver",
                new=mock_webdriver,
                create=True,
            ),
            patch(
                "chemtabextract.input.from_html.FirefoxOptions",
                new=MagicMock,
                create=True,
            ),
        ):
            result = configure_selenium()

        mock_webdriver.Firefox.assert_called_once()
        assert result is fake_driver

    def test_configure_selenium_returns_none_for_unknown_browser(self) -> None:
        """Should return None for any browser name other than 'Firefox'."""
        result = configure_selenium(browser="Chrome")
        assert result is None
