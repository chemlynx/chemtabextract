"""Shared pytest fixtures for the chemtabextract test suite."""

import pytest

from chemtabextract import Table


@pytest.fixture
def table_example1():
    """Table instance from the primary example CSV."""
    return Table("./tests/data/table_example1.csv")


@pytest.fixture
def table_example2():
    return Table("./tests/data/table_example2.csv")


@pytest.fixture
def table_example3():
    return Table("./tests/data/table_example3.csv")


@pytest.fixture
def table_example4():
    return Table("./tests/data/table_example4.csv")


@pytest.fixture
def table_example5():
    return Table("./tests/data/table_example5.csv")


@pytest.fixture
def table_example6():
    return Table("./tests/data/table_example6.csv")


@pytest.fixture
def table_example7():
    return Table("./tests/data/table_example7.csv")


@pytest.fixture
def table_example8():
    return Table("./tests/data/table_example8.csv")


@pytest.fixture
def table_example9():
    return Table("./tests/data/table_example9.csv")


@pytest.fixture
def table_example10():
    return Table("./tests/data/table_example10.csv")


@pytest.fixture
def table_example11():
    return Table("./tests/data/table_example11.csv")


@pytest.fixture
def table_example12():
    return Table("./tests/data/table_example12.csv")


@pytest.fixture
def table_example13():
    return Table("./tests/data/table_example13.csv")
