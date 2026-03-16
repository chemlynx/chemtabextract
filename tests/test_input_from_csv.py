"""
chemtabextract.tests.test_input_from_csv.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test table parsers.
Juraj Mavračić (jm2111@cam.ac.uk)
Ed Beard (ejb207@cam.ac.uk)
"""

import logging
import os

from chemtabextract import Table

log = logging.getLogger(__name__)


def test_input_with_commas():
    path = os.path.join(os.path.dirname(__file__), "data", "table_commas.csv")
    table = Table(path)

    table.print()
    assert table.raw_table[0][6] == "PCE (η, %)"
    assert table.raw_table[1][0] == "2H–MoS2 (hydrothermal, 200 °C)"
    assert table.raw_table[2][0] == "1T–MoS2 (hydrothermal, 180 °C)"


def test_input_with_double_quotes():
    path = os.path.join(os.path.dirname(__file__), "data", "table_double_quotes.csv")
    table = Table(path)

    assert table.raw_table[1][0] == 'N719 "cell'
    assert table.raw_table[3][0] == 'Hy"brid cell'


def test_input_with_single_quotes():
    path = os.path.join(os.path.dirname(__file__), "data", "table_single_quotes.csv")
    table = Table(path)

    assert table.raw_table[1][0] == "N719 'cell"
    assert table.raw_table[2][0] == "N74'9 cell"
    assert table.raw_table[3][2] == "13'.8"


def test_input_with_blank_lines():
    path = os.path.join(os.path.dirname(__file__), "data", "table_empty_lines.csv")
    table = Table(path)

    assert table.raw_table[0][6] == "PCE (η, %)"
    assert table.raw_table[1][0] == "2H–MoS2 (hydrothermal, 200 °C)"
    assert table.raw_table[2][0] == "1T–MoS2 (hydrothermal, 180 °C)"


def test_table_with_broken_rows():
    path = os.path.join(os.path.dirname(__file__), "data", "table_broken_row.csv")
    table = Table(path)

    assert len(table.category_table) == 10
