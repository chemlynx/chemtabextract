"""Tests for chemtabextract.input.from_list.read.

Covers the dynamic dtype computation introduced in Q7, which replaced the
hard-coded ``dtype="<U60"`` that silently truncated cell values longer than
60 characters.
"""

import logging

import numpy as np
import pytest

from chemtabextract.input import from_list


class TestFromListDynamicDtype:
    """from_list.read() computes dtype width from actual cell content (Q7).

    Before Q7 the dtype was hard-coded to ``<U60``, silently truncating any
    cell value longer than 60 characters.  After Q7 the dtype is derived from
    the maximum cell length so that no truncation can occur.
    """

    def test_cells_longer_than_60_chars_stored_in_full(self) -> None:
        """A cell with 100 characters must survive the read() call without truncation."""
        long_cell = "A" * 100  # exceeds the old <U60 limit
        result = from_list.read([["header", "col2"], [long_cell, "short"]])
        assert result[1, 0] == long_cell

    def test_dtype_width_matches_longest_cell(self) -> None:
        """The array dtype itemsize should accommodate the longest cell exactly."""
        long_cell = "B" * 75
        result = from_list.read([["short", long_cell], ["x", "y"]])
        # Each Unicode character occupies 4 bytes in a NumPy fixed-width dtype.
        assert result.dtype.itemsize == 75 * 4

    def test_truncation_warning_logged_for_cells_over_200_chars(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A WARNING-level log entry must be emitted when any cell exceeds 200 chars."""
        oversized_cell = "C" * 201
        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_list"):
            from_list.read([["header"], [oversized_cell]])

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("201" in msg for msg in warning_messages)

    def test_no_warning_for_cells_at_or_below_200_chars(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """No warning should be logged when all cells are at or below 200 characters."""
        cell_200 = "D" * 200  # exactly at the threshold — must not warn
        with caplog.at_level(logging.WARNING, logger="chemtabextract.input.from_list"):
            from_list.read([["header"], [cell_200]])

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert not warning_messages

    def test_result_is_numpy_ndarray_with_unicode_dtype(self) -> None:
        """read() must return a numpy array with a Unicode string dtype."""
        result = from_list.read([["a", "b"], ["1", "2"]])
        assert isinstance(result, np.ndarray)
        assert np.issubdtype(result.dtype, np.str_)

    def test_jagged_rows_padded_to_longest(self) -> None:
        """Rows shorter than the longest row must be padded so the array is rectangular."""
        result = from_list.read([["a", "b", "c"], ["x"]])
        assert result.shape == (2, 3)
