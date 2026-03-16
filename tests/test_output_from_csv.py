# -*- coding: utf-8 -*-
"""
chemtabextract.tests.test_output_from_csv.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test csv table output parser.
Ed Beard (ejb207@cam.ac.uk)
"""

import logging
import os

from chemtabextract import Table
from chemtabextract.output.to_csv import write_to_csv

log = logging.getLogger(__name__)


def _do_conversion(filename: str) -> None:
    """Helper: round-trip a CSV file through Table and write_to_csv."""
    in_path = os.path.join(os.path.dirname(__file__), "data", filename)
    out_path = os.path.join(os.path.dirname(__file__), "data", "temp_" + filename)

    with open(in_path, "r", encoding="utf-8") as f:
        in_string = f.read()
    table = Table(in_path)

    write_to_csv(table.raw_table, out_path)
    with open(in_path, "r", encoding="utf-8") as f:
        out_string = f.read()
    os.remove(out_path)

    assert in_string == out_string


def test_table_example1():
    _do_conversion("table_example1.csv")


def test_table_double_quotes():
    _do_conversion("table_double_quotes.csv")


def test_all_example_tables():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    for file in os.listdir(data_dir):
        _do_conversion(file)
