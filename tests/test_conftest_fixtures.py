"""Smoke tests that inject every conftest.py fixture via pytest parameter injection.

Each test verifies that the fixture:
1. Is not None (the Table constructed successfully).
2. Has a category_table attribute (the full analysis pipeline completed).
3. Has a non-empty pre_cleaned_table (the source data was loaded).

This file exists to satisfy TC3 from IMPROVEMENTS.md: every shared fixture
defined in conftest.py must be used by at least one test function via pytest's
fixture injection mechanism, not just constructed inline.

Tests are intentionally minimal — they are smoke tests, not semantic assertions
about specific cell values.  Semantic coverage for individual tables lives in
the specialist test files (test_table_table.py, test_table_table_subtables.py,
etc.).
"""

import numpy as np

from chemtabextract import Table


def _assert_table_ok(table: Table) -> None:
    """Common postconditions for a successfully constructed Table."""
    assert table is not None
    assert isinstance(table.pre_cleaned_table, np.ndarray)
    assert table.pre_cleaned_table.size > 0
    assert table.category_table is not None


class TestConftestFixtures:
    """Inject every conftest fixture and verify basic postconditions."""

    def test_table_example1_loads(self, table_example1: Table) -> None:
        """table_example1 fixture should produce a valid Table."""
        _assert_table_ok(table_example1)

    def test_table_example2_loads(self, table_example2: Table) -> None:
        """table_example2 fixture should produce a valid Table."""
        _assert_table_ok(table_example2)

    def test_table_example3_loads(self, table_example3: Table) -> None:
        """table_example3 fixture should produce a valid Table."""
        _assert_table_ok(table_example3)

    def test_table_example4_loads(self, table_example4: Table) -> None:
        """table_example4 fixture should produce a valid Table."""
        _assert_table_ok(table_example4)

    def test_table_example5_loads(self, table_example5: Table) -> None:
        """table_example5 fixture should produce a valid Table."""
        _assert_table_ok(table_example5)

    def test_table_example6_loads(self, table_example6: Table) -> None:
        """table_example6 fixture should produce a valid Table."""
        _assert_table_ok(table_example6)

    def test_table_example7_loads(self, table_example7: Table) -> None:
        """table_example7 fixture should produce a valid Table."""
        _assert_table_ok(table_example7)

    def test_table_example8_loads(self, table_example8: Table) -> None:
        """table_example8 fixture should produce a valid Table."""
        _assert_table_ok(table_example8)

    def test_table_example9_loads(self, table_example9: Table) -> None:
        """table_example9 fixture should produce a valid Table."""
        _assert_table_ok(table_example9)

    def test_table_example10_loads(self, table_example10: Table) -> None:
        """table_example10 fixture should produce a valid Table."""
        _assert_table_ok(table_example10)

    def test_table_example11_loads(self, table_example11: Table) -> None:
        """table_example11 fixture should produce a valid Table."""
        _assert_table_ok(table_example11)

    def test_table_example12_loads(self, table_example12: Table) -> None:
        """table_example12 fixture should produce a valid Table."""
        _assert_table_ok(table_example12)

    def test_table_example13_loads(self, table_example13: Table) -> None:
        """table_example13 fixture should produce a valid Table."""
        _assert_table_ok(table_example13)
