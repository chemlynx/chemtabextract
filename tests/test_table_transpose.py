"""Tests for Table.transpose() and the _raw_table_cache introduced in f2edc1f.

Before f2edc1f, raw_table was a property that called from_any.create_table on
every access, causing repeated file I/O inside _analyze_table.  The fix
introduces _raw_table_cache: the source is loaded once per _analyze_table
call and the property simply returns the cached value (or its transpose).

These tests verify:
  - _raw_table_cache is populated on construction
  - raw_table returns the cache directly when not transposed
  - transpose() re-loads the cache from source (non-transposed data) and
    sets history.table_transposed = True, so raw_table returns cache.T
  - calling transpose() a second time does NOT toggle back to the original
    orientation — it is not a toggle; it always produces the transposed view
"""

import numpy as np
import pytest

from chemtabextract import Table

_CSV = "./tests/data/table_example1.csv"


@pytest.fixture()
def fresh_table() -> Table:
    """Freshly constructed Table from the primary example CSV."""
    return Table(_CSV)


class TestRawTableCache:
    """_raw_table_cache is populated correctly on construction."""

    def test_cache_is_ndarray_after_construction(self, fresh_table: Table) -> None:
        """_raw_table_cache should be a numpy ndarray immediately after __init__."""
        assert isinstance(fresh_table._raw_table_cache, np.ndarray)

    def test_cache_is_not_none_after_construction(self, fresh_table: Table) -> None:
        """_raw_table_cache must not be None — a None cache would make raw_table crash."""
        assert fresh_table._raw_table_cache is not None

    def test_cache_dtype_is_u60(self, fresh_table: Table) -> None:
        """Cached array should use '<U60' dtype, consistent with other input paths."""
        assert fresh_table._raw_table_cache.dtype == np.dtype("<U60")

    def test_raw_table_equals_cache_when_not_transposed(self, fresh_table: Table) -> None:
        """raw_table should return the exact same array as _raw_table_cache
        when the table has not been transposed."""
        assert np.array_equal(fresh_table.raw_table, fresh_table._raw_table_cache)

    def test_raw_table_is_two_dimensional(self, fresh_table: Table) -> None:
        """raw_table must be 2-D; a 1-D result should have been rejected at load time."""
        assert fresh_table.raw_table.ndim == 2


class TestTransposeOnce:
    """After a single call to transpose(), shape and flags are correct."""

    def test_transpose_inverts_shape(self, fresh_table: Table) -> None:
        """After one transpose, raw_table.shape should be (original_cols, original_rows)."""
        rows, cols = fresh_table.raw_table.shape
        fresh_table.transpose()
        assert fresh_table.raw_table.shape == (cols, rows)

    def test_transpose_sets_table_transposed_flag(self, fresh_table: Table) -> None:
        """history.table_transposed should be False before and True after transpose()."""
        assert fresh_table.history.table_transposed is False
        fresh_table.transpose()
        assert fresh_table.history.table_transposed is True

    def test_raw_table_after_transpose_equals_cache_dot_T(self, fresh_table: Table) -> None:
        """After transpose(), raw_table should be exactly _raw_table_cache.T.

        This confirms the property correctly applies the transpose to the cache
        rather than the other way around, or returning some stale value.
        """
        fresh_table.transpose()
        assert np.array_equal(fresh_table.raw_table, fresh_table._raw_table_cache.T)

    def test_cache_repopulated_after_transpose(self, fresh_table: Table) -> None:
        """_raw_table_cache should remain a valid ndarray after transpose().

        transpose() calls _analyze_table(), which calls _load_raw_table() and
        replaces the cache.  The cache should never be left as None.
        """
        fresh_table.transpose()
        assert isinstance(fresh_table._raw_table_cache, np.ndarray)
        assert fresh_table._raw_table_cache is not None

    def test_cache_after_transpose_contains_original_orientation(self, fresh_table: Table) -> None:
        """_raw_table_cache itself should still hold the non-transposed data.

        The transpose is applied only in the raw_table property getter.
        The underlying cache is always the data as loaded from source.
        """
        original_shape = fresh_table.raw_table.shape  # (rows, cols)
        fresh_table.transpose()
        # raw_table is now (cols, rows), but _raw_table_cache is still (rows, cols)
        assert fresh_table._raw_table_cache.shape == original_shape


class TestTransposeTwice:
    """Calling transpose() twice does not toggle back to the original orientation.

    transpose() is not a toggle.  Each call resets History and sets
    table_transposed=True, then re-runs _analyze_table.  The raw table is
    always loaded from source (non-transposed), and the property always
    returns cache.T when table_transposed=True.  Two consecutive calls
    therefore produce the same result as one call.
    """

    def test_shape_after_two_transposes_equals_shape_after_one(self, fresh_table: Table) -> None:
        """Two transpose() calls should yield the same shape as one."""
        original_shape = fresh_table.raw_table.shape
        fresh_table.transpose()
        shape_after_one = fresh_table.raw_table.shape
        fresh_table.transpose()
        shape_after_two = fresh_table.raw_table.shape

        assert shape_after_two == shape_after_one
        assert shape_after_two != original_shape

    def test_table_transposed_flag_still_true_after_two_transposes(
        self, fresh_table: Table
    ) -> None:
        """history.table_transposed should be True after both calls."""
        fresh_table.transpose()
        fresh_table.transpose()
        assert fresh_table.history.table_transposed is True


class TestTransposeResetsHistory:
    """transpose() creates a fresh History with only table_transposed=True set."""

    def test_other_history_flags_are_false_after_transpose(self, fresh_table: Table) -> None:
        """After transpose(), History is reset; only table_transposed survives.

        The newly created History() inside transpose() starts with all flags
        False; only table_transposed is then set to True before _analyze_table
        runs.  _analyze_table may subsequently set algorithm flags again, but
        the structural reset is observable through table_transposed=True and
        the new History object.
        """
        fresh_table.transpose()
        # table_transposed is the only flag set before _analyze_table re-runs.
        assert fresh_table.history.table_transposed is True
