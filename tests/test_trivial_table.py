"""
Tests the TrivialTable object.

.. codeauthor: Juraj Mavračić <jm2111@cam.ac.uk>
"""

import logging

from chemtabextract import TrivialTable

log = logging.getLogger(__name__)


def test_default_config():
    """Trivial Table test. One row for column header and one column for row header."""
    table = TrivialTable("./tests/data/row_categories_table.csv")

    table.print()
    category_table = [
        ["293", ["Gd"], ["TC (K)"]],
        ["5", ["Gd"], ["ΔH (T)"]],
        ["9.5", ["Gd"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["410", ["Gd"], ["RCP (J kg−1)"]],
        ["52–55", ["Gd"], ["Ref."]],
        ["293", ["Gd"], ["TC (K)"]],
        ["1", ["Gd"], ["ΔH (T)"]],
        ["3.25", ["Gd"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["—", ["Gd"], ["RCP (J kg−1)"]],
        ["56", ["Gd"], ["Ref."]],
        ["337", ["La2 (PWD)"], ["TC (K)"]],
        ["1", ["La2 (PWD)"], ["ΔH (T)"]],
        ["2.70", ["La2 (PWD)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["68", ["La2 (PWD)"], ["RCP (J kg−1)"]],
        ["57", ["La2 (PWD)"], ["Ref."]],
        ["292", ["La0.67Ba0.33 (TF)"], ["TC (K)"]],
        ["5", ["La0.67Ba0.33 (TF)"], ["ΔH (T)"]],
        ["1.48", ["La0.67Ba0.33 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["161", ["La0.67Ba0.33 (TF)"], ["RCP (J kg−1)"]],
        ["26", ["La0.67Ba0.33 (TF)"], ["Ref."]],
        ["252", ["La0.67Ca0.33 (TF)"], ["TC (K)"]],
        ["5", ["La0.67Ca0.33 (TF)"], ["ΔH (T)"]],
        ["2.08", ["La0.67Ca0.33 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["175", ["La0.67Ca0.33 (TF)"], ["RCP (J kg−1)"]],
        ["26", ["La0.67Ca0.33 (TF)"], ["Ref."]],
        ["312", ["La0.67Sr0.33MnO3 (TF)"], ["TC (K)"]],
        ["1.5", ["La0.67Sr0.33MnO3 (TF)"], ["ΔH (T)"]],
        ["1.54", ["La0.67Sr0.33MnO3 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["50.16", ["La0.67Sr0.33MnO3 (TF)"], ["RCP (J kg−1)"]],
        ["58", ["La0.67Sr0.33MnO3 (TF)"], ["Ref."]],
        ["321", ["La0.67Sr0.33MnO3 (TF)"], ["TC (K)"]],
        ["1.5", ["La0.67Sr0.33MnO3 (TF)"], ["ΔH (T)"]],
        ["1.47", ["La0.67Sr0.33MnO3 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["34.24", ["La0.67Sr0.33MnO3 (TF)"], ["RCP (J kg−1)"]],
        ["58", ["La0.67Sr0.33MnO3 (TF)"], ["Ref."]],
        ["309", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["TC (K)"]],
        ["1", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["ΔH (T)"]],
        ["0.93", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["45", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["RCP (J kg−1)"]],
        ["39", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["Ref."]],
        ["309", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["TC (K)"]],
        ["5", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["ΔH (T)"]],
        ["3.19", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["307", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["RCP (J kg−1)"]],
        ["39", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["Ref."]],
        ["286", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["TC (K)"]],
        ["5", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["ΔH (T)"]],
        ["3.35", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["220", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["RCP (J kg−1)"]],
        ["This work", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["Ref."]],
        ["286", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["TC (K)"]],
        ["1", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["ΔH (T)"]],
        ["0.99", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["49", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["RCP (J kg−1)"]],
        ["This work", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["Ref."]],
    ]
    labels = [
        ["StubHeader", "ColHeader", "ColHeader", "ColHeader", "ColHeader", "ColHeader"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
        ["RowHeader", "Data", "Data", "Data", "Data", "Data"],
    ]
    assert category_table == table.category_table
    assert labels == table.labels.tolist()


# ---------------------------------------------------------------------------
# TC2: TrivialTable.col_header / row_header with degenerate table sizes
# ---------------------------------------------------------------------------


def test_trivial_table_col_header_single_row_does_not_raise() -> None:
    """TrivialTable.col_header should not raise for a single-row table.

    A CSV with exactly one data row exercises the edge of TrivialTable's
    critical-cell calculation.  With defaults (col_header=0, row_header=0),
    the result may be an empty array but must not raise any exception.
    """
    table = TrivialTable("./tests/data/table_1row.csv")
    result = table.col_header  # must not raise
    # Result is either None (if _critical_cells is False) or a numpy array.
    assert result is None or hasattr(result, "shape")


def test_trivial_table_row_header_single_row_does_not_raise() -> None:
    """TrivialTable.row_header should not raise for a single-row table."""
    table = TrivialTable("./tests/data/table_1row.csv")
    result = table.row_header  # must not raise
    assert result is None or hasattr(result, "shape")


def test_trivial_table_col_header_single_col_does_not_raise() -> None:
    """TrivialTable.col_header should not raise for a single-column table."""
    table = TrivialTable("./tests/data/table_1col.csv")
    result = table.col_header  # must not raise
    assert result is None or hasattr(result, "shape")


def test_trivial_table_row_header_single_col_does_not_raise() -> None:
    """TrivialTable.row_header should not raise for a single-column table."""
    table = TrivialTable("./tests/data/table_1col.csv")
    result = table.row_header  # must not raise
    assert result is None or hasattr(result, "shape")
