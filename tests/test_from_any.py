"""Tests for chemtabextract.input.from_any predicate functions.

html() and csv() were migrated from os.path.isfile to Path.is_file() in the
post-verify-cleanups fix (S1).  These tests provide a regression guard for
that change and cover the True/False branches of both functions.
"""

from pathlib import Path

from chemtabextract.input.from_any import csv, html


class TestHtmlPredicate:
    """Tests for from_any.html()."""

    def test_existing_html_file_returns_true(self, tmp_path: Path) -> None:
        """html() should return True for a file that exists and ends with .html."""
        f = tmp_path / "table.html"
        f.write_text("<html></html>", encoding="utf-8")
        assert html(str(f)) is True

    def test_nonexistent_html_path_returns_false(self, tmp_path: Path) -> None:
        """html() should return False when the file does not exist."""
        assert html(str(tmp_path / "missing.html")) is False

    def test_existing_file_wrong_extension_returns_false(self, tmp_path: Path) -> None:
        """html() should return False when the file exists but is not .html."""
        f = tmp_path / "table.csv"
        f.write_text("a,b", encoding="utf-8")
        assert html(str(f)) is False

    def test_empty_string_returns_false(self) -> None:
        """html() should return False for an empty string without raising."""
        assert html("") is False

    def test_url_string_returns_false(self) -> None:
        """html() should return False for a URL (no local file exists at that path)."""
        assert html("http://example.com/table.html") is False


class TestCsvPredicate:
    """Tests for from_any.csv()."""

    def test_existing_csv_file_returns_true(self, tmp_path: Path) -> None:
        """csv() should return True for a file that exists and ends with .csv."""
        f = tmp_path / "data.csv"
        f.write_text("a,b\n1,2\n", encoding="utf-8")
        assert csv(str(f)) is True

    def test_nonexistent_csv_path_returns_false(self, tmp_path: Path) -> None:
        """csv() should return False when the file does not exist."""
        assert csv(str(tmp_path / "missing.csv")) is False

    def test_existing_file_wrong_extension_returns_false(self, tmp_path: Path) -> None:
        """csv() should return False when the file exists but is not .csv."""
        f = tmp_path / "data.html"
        f.write_text("<html></html>", encoding="utf-8")
        assert csv(str(f)) is False

    def test_empty_string_returns_false(self) -> None:
        """csv() should return False for an empty string without raising."""
        assert csv("") is False

    def test_url_string_returns_false(self) -> None:
        """csv() should return False for a URL (no local file exists at that path)."""
        assert csv("http://example.com/data.csv") is False
