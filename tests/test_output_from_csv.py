"""Tests for CSV output (write_to_csv round-trip).

Each parametrised case reads a source CSV, round-trips it through
Table → write_to_csv, then compares the output file against the original.

Known production defects (tracked as xfail):
    write_to_csv does not always reproduce the source CSV byte-for-byte.
    Observed differences include:
      - Quoting style: source may use explicit ``"",""`` for empty fields;
        csv.writer (QUOTE_MINIMAL) writes bare ``,,`` instead.
      - Certain source files contain content that does not survive a
        raw_table round-trip (e.g. table_broken_row.csv drops a broken row).
    These are marked xfail(strict=True) so that they become visible XPASS
    failures the moment write_to_csv is corrected, prompting removal of the
    marker.  See https://github.com/chemlynx/tabledataextractor for tracker.
"""

from pathlib import Path

import pytest

from chemtabextract import Table
from chemtabextract.output.to_csv import write_to_csv

_DATA = Path(__file__).parent / "data"

# Files where write_to_csv does not reproduce the source byte-for-byte.
# Reason is documented per entry for clarity.
_ROUND_TRIP_FAILURES: dict[str, str] = {
    "table_broken_row.csv": (
        "broken/jagged rows are normalised by raw_table; output row count differs"
    ),
    "table_example1.csv": (
        'source uses explicit quoted-empty fields ("",""); '
        "csv.writer QUOTE_MINIMAL writes bare empty (,,)"
    ),
    "table_example7.csv": (
        "source uses explicit quoted-empty fields; csv.writer writes bare empty"
    ),
    "te_01.csv": ("source uses explicit quoted-empty fields; csv.writer writes bare empty"),
    "te_02.csv": ("source uses explicit quoted-empty fields; csv.writer writes bare empty"),
    "te_03.csv": ("source uses explicit quoted-empty fields; csv.writer writes bare empty"),
    "te_04.csv": ("source uses explicit quoted-empty fields; csv.writer writes bare empty"),
    "te_05.csv": ("source uses explicit quoted-empty fields; csv.writer writes bare empty"),
}

_ALL_CSV = sorted(p.name for p in _DATA.glob("*.csv"))


def _parametrize_csv_files():
    """Build parametrize list, attaching xfail markers to known failures."""
    params = []
    for name in _ALL_CSV:
        if name in _ROUND_TRIP_FAILURES:
            params.append(
                pytest.param(
                    name,
                    marks=pytest.mark.xfail(
                        strict=True,
                        reason=_ROUND_TRIP_FAILURES[name],
                    ),
                )
            )
        else:
            params.append(name)
    return params


def _do_conversion(filename: str, tmp_path: Path) -> None:
    """Round-trip a CSV through Table → write_to_csv and assert identical content.

    Args:
        filename: Bare filename (no directory) of the source CSV.
        tmp_path: Pytest-provided temporary directory for the output file.
    """
    in_path = _DATA / filename
    out_path = tmp_path / filename

    with open(in_path, encoding="utf-8") as f:
        in_string = f.read()

    table = Table(str(in_path))
    write_to_csv(table.raw_table, str(out_path))

    with open(out_path, encoding="utf-8") as f:  # read the OUTPUT, not the input
        out_string = f.read()

    assert in_string == out_string


@pytest.mark.parametrize("filename", _parametrize_csv_files())
def test_csv_round_trip(filename: str, tmp_path: Path) -> None:
    """Round-tripping each CSV through Table and write_to_csv should reproduce it exactly."""
    _do_conversion(filename, tmp_path)


def test_write_to_csv_overwrites_existing_file(tmp_path: Path) -> None:
    """write_to_csv should silently overwrite a pre-existing file at the target path."""
    src = str(_DATA / "table_double_quotes.csv")
    out_path = tmp_path / "out.csv"

    # Pre-populate the target with a sentinel so we can confirm it is overwritten
    out_path.write_text("old content", encoding="utf-8")

    table = Table(src)
    write_to_csv(table.raw_table, str(out_path))

    result = out_path.read_text(encoding="utf-8")
    assert result != "old content", "write_to_csv did not overwrite the existing file"
