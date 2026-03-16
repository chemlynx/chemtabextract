"""
Tests the row categories table.

.. codeauthor: Juraj Mavračić <jm2111@cam.ac.uk>
"""

import logging

from chemtabextract import Table

log = logging.getLogger(__name__)


def test_default_config():
    table = Table("./tests/data/row_categories_table.csv")

    table.print()
    category_table = [
        ["9.5", ["Gd", "293", "5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["410", ["Gd", "293", "5"], ["RCP (J kg−1)"]],
        ["52–55", ["Gd", "293", "5"], ["Ref."]],
        ["3.25", ["Gd", "293", "1"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["NoValue", ["Gd", "293", "1"], ["RCP (J kg−1)"]],
        ["56", ["Gd", "293", "1"], ["Ref."]],
        ["2.70", ["La2 (PWD)", "337", "1"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["68", ["La2 (PWD)", "337", "1"], ["RCP (J kg−1)"]],
        ["57", ["La2 (PWD)", "337", "1"], ["Ref."]],
        ["1.48", ["La0.67Ba0.33 (TF)", "292", "5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["161", ["La0.67Ba0.33 (TF)", "292", "5"], ["RCP (J kg−1)"]],
        ["26", ["La0.67Ba0.33 (TF)", "292", "5"], ["Ref."]],
        ["2.08", ["La0.67Ca0.33 (TF)", "252", "5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["175", ["La0.67Ca0.33 (TF)", "252", "5"], ["RCP (J kg−1)"]],
        ["26", ["La0.67Ca0.33 (TF)", "252", "5"], ["Ref."]],
        ["1.54", ["La0.67Sr0.33MnO3 (TF)", "312", "1.5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["50.16", ["La0.67Sr0.33MnO3 (TF)", "312", "1.5"], ["RCP (J kg−1)"]],
        ["58", ["La0.67Sr0.33MnO3 (TF)", "312", "1.5"], ["Ref."]],
        ["1.47", ["La0.67Sr0.33MnO3 (TF)", "321", "1.5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["34.24", ["La0.67Sr0.33MnO3 (TF)", "321", "1.5"], ["RCP (J kg−1)"]],
        ["58", ["La0.67Sr0.33MnO3 (TF)", "321", "1.5"], ["Ref."]],
        ["0.93", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "1"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["45", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "1"], ["RCP (J kg−1)"]],
        ["39", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "1"], ["Ref."]],
        ["3.19", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["307", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "5"], ["RCP (J kg−1)"]],
        ["39", ["Ba0.33Mn0.98Ti0.02O3 (PWD)", "309", "5"], ["Ref."]],
        ["3.35", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "5"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["220", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "5"], ["RCP (J kg−1)"]],
        ["This work", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "5"], ["Ref."]],
        ["0.99", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "1"], ["−(ΔSM)max (J kg−1 K−1)"]],
        ["49", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "1"], ["RCP (J kg−1)"]],
        ["This work", ["Ba0.33Mn0.98Ti0.02O3 (TF)", "286", "1"], ["Ref."]],
    ]
    labels = [
        ["StubHeader", "StubHeader", "StubHeader", "ColHeader", "ColHeader", "ColHeader"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
        ["RowHeader", "RowHeader", "RowHeader", "Data", "Data", "Data"],
    ]
    assert category_table == table.category_table
    assert labels == table.labels.tolist()

    # Row categories
    table = table.row_categories
    table.print()
    category_table = [
        ["293", ["Gd"], ["TC (K)"]],
        ["5", ["Gd"], ["ΔH (T)"]],
        ["293", ["Gd"], ["TC (K)"]],
        ["1", ["Gd"], ["ΔH (T)"]],
        ["337", ["La2 (PWD)"], ["TC (K)"]],
        ["1", ["La2 (PWD)"], ["ΔH (T)"]],
        ["292", ["La0.67Ba0.33 (TF)"], ["TC (K)"]],
        ["5", ["La0.67Ba0.33 (TF)"], ["ΔH (T)"]],
        ["252", ["La0.67Ca0.33 (TF)"], ["TC (K)"]],
        ["5", ["La0.67Ca0.33 (TF)"], ["ΔH (T)"]],
        ["312", ["La0.67Sr0.33MnO3 (TF)"], ["TC (K)"]],
        ["1.5", ["La0.67Sr0.33MnO3 (TF)"], ["ΔH (T)"]],
        ["321", ["La0.67Sr0.33MnO3 (TF)"], ["TC (K)"]],
        ["1.5", ["La0.67Sr0.33MnO3 (TF)"], ["ΔH (T)"]],
        ["309", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["TC (K)"]],
        ["1", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["ΔH (T)"]],
        ["309", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["TC (K)"]],
        ["5", ["Ba0.33Mn0.98Ti0.02O3 (PWD)"], ["ΔH (T)"]],
        ["286", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["TC (K)"]],
        ["5", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["ΔH (T)"]],
        ["286", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["TC (K)"]],
        ["1", ["Ba0.33Mn0.98Ti0.02O3 (TF)"], ["ΔH (T)"]],
    ]
    labels = [
        ["StubHeader", "ColHeader", "ColHeader"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
        ["RowHeader", "Data", "Data"],
    ]
    assert category_table == table.category_table
    assert labels == table.labels.tolist()

    # Row categories of row categories
    table = table.row_categories
    table.print()
    category_table = [
        ["Gd", [""], ["Composition"]],
        ["La2 (PWD)", [""], ["Composition"]],
        ["La0.67Ba0.33 (TF)", [""], ["Composition"]],
        ["La0.67Ca0.33 (TF)", [""], ["Composition"]],
        ["La0.67Sr0.33MnO3 (TF)", [""], ["Composition"]],
        ["Ba0.33Mn0.98Ti0.02O3 (PWD)", [""], ["Composition"]],
        ["Ba0.33Mn0.98Ti0.02O3 (TF)", [""], ["Composition"]],
    ]
    labels = [["ColHeader"], ["Data"], ["Data"], ["Data"], ["Data"], ["Data"], ["Data"], ["Data"]]
    assert category_table == table.category_table
    assert labels == table.labels.tolist()

    # Row categories of row categories of row categories
    table = table.row_categories
    assert table is None
