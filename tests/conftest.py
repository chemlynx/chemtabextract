"""Shared pytest fixtures for the chemtabextract test suite."""

import pytest

from chemtabextract import Table


@pytest.fixture
def table_example1():
    """Table instance from the primary example CSV.

    8 columns × many rows.  Computational crystal-structure data with a
    two-level column header (crystal phase / parameter) and two-level row
    header (method / source).  Used extensively in TestTableConfigsProperty,
    TestOverrideConfig, and header-extension tests.
    """
    return Table("./tests/data/table_example1.csv")


@pytest.fixture
def table_example2():
    """Government-transfers table with multi-year column groups.

    6 columns × several rows.  Three-level column header (year / transfer
    type / metric) and a simple row header.  Tests multi-level header
    detection.
    """
    return Table("./tests/data/table_example2.csv")


@pytest.fixture
def table_example3():
    """Official development assistance (ODA) by country.

    11 columns × many rows.  Two-level column header (metric / year) and a
    country name row header.  Features footnote markers (asterisks) in column
    headers.
    """
    return Table("./tests/data/table_example3.csv")


@pytest.fixture
def table_example4():
    """Mobile-messaging statistics — simple 5-column table.

    5 columns × several rows.  Single row of column headers; year-based row
    header.  Useful baseline for simple prefixing and category extraction.
    """
    return Table("./tests/data/table_example4.csv")


@pytest.fixture
def table_example5():
    """Mobile-messaging statistics with a two-level column header.

    6 columns × several rows.  Two-level column header (group / metric) and a
    year-based row header.  Used in header-extension (downward) tests.
    """
    return Table("./tests/data/table_example5.csv")


@pytest.fixture
def table_example6():
    """Two-column material/Tc table with a single-level header.

    4 columns × several rows presenting material names and critical
    temperatures.  Tests side-by-side identical structures (candidate for
    subtable splitting).
    """
    return Table("./tests/data/table_example6.csv")


@pytest.fixture
def table_example7():
    """ODA table with a repeated title block at the start.

    14 columns × many rows.  Contains a repeated header section that exercises
    footnote and title-row detection.
    """
    return Table("./tests/data/table_example7.csv")


@pytest.fixture
def table_example8():
    """Mobile-messaging table with a full-width title row.

    6 columns × several rows.  First row is a spanning title ("Table 9. …");
    exercises title-row detection and removal.
    """
    return Table("./tests/data/table_example8.csv")


@pytest.fixture
def table_example9():
    """Transposed mobile-messaging table — data in columns, years as headers.

    3 columns × several rows.  Title row present; data and year values placed
    in column orientation.  Tests transposition-oriented analysis.
    """
    return Table("./tests/data/table_example9.csv")


@pytest.fixture
def table_example10():
    """Mobile-messaging table with sub-group row in the column header.

    6 columns × several rows.  Three-level column header including a sub-group
    row that uses sparse labels (A, B) at alternating positions.
    """
    return Table("./tests/data/table_example10.csv")


@pytest.fixture
def table_example11():
    """Mobile-messaging table with title row and two-level column groups.

    6 columns × several rows.  First row is a spanning title; second row
    contains two group labels (Category A, Category B).  Exercises title-row
    removal combined with multi-level header detection.
    """
    return Table("./tests/data/table_example11.csv")


@pytest.fixture
def table_example12():
    """Mobile-messaging table transposed with a combined title/row-header column.

    5 columns × several rows.  Data is laid out with years as column headers
    and metrics as row headers; a combined title cell occupies the stub-header
    position.
    """
    return Table("./tests/data/table_example12.csv")


@pytest.fixture
def table_example13():
    """As–Cu–Te amorphous alloy coordination-number data.

    6 columns × several rows.  Each cell contains values with uncertainties
    ("1.82 ± 0.3").  Row header is bond type (NAsAs, NAsCu, …); column
    header is alloy composition.  Tests Unicode cell content and numeric
    precision handling.
    """
    return Table("./tests/data/table_example13.csv")
