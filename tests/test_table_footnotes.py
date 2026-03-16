"""
Test Footnote() class on some input tables.
These tests depend on some of the features of Table() working properly.
Juraj Mavračić (jm2111@cam.ac.uk)
"""

import logging

import numpy as np

from chemtabextract import Table

log = logging.getLogger(__name__)


class TableF(Table):
    """Derivative of Table used to isolate testing for Footnotes()"""

    def __init__(self, file_path, table_number=1, **kwargs):
        super().__init__(file_path, table_number, **kwargs)

    @property
    def labels(self):
        """Cell labels. Python List"""
        temp = np.empty_like(self._pre_cleaned_table, dtype="<U60")
        temp[:, :] = "/"
        temp[self._cc4] = "CC4"

        for footnote in self.footnotes:
            temp[footnote.prefix_cell[0], footnote.prefix_cell[1]] = "FNprefix"
            if footnote.text_cell is not None:
                temp[footnote.text_cell[0], footnote.text_cell[1]] = (
                    "FNtext"
                    if temp[footnote.text_cell[0], footnote.text_cell[1]] == "/"
                    else "FNprefix & FNtext"
                )
            for ref_cell in footnote.reference_cells:
                temp[ref_cell[0], ref_cell[1]] = (
                    "FNref"
                    if temp[ref_cell[0], ref_cell[1]] == "/"
                    else temp[ref_cell[0], ref_cell[1]] + " & FNref"
                )
        return temp


def test_table_use_footnotes():
    table = TableF(
        "./tests/data/table_example_footnotes.csv", use_footnotes=True, use_spanning_cells=False
    )
    table.print()

    fn = table.footnotes[0]
    print(fn)
    assert fn.prefix == "c"
    assert fn.text == "Footnote text."
    assert fn.references == ["OECD/DAC c"]

    fn = table.footnotes[1]
    print(fn)
    assert fn.prefix == "*"
    assert fn.text == "Test"
    assert fn.references == ["2010*", "2011* a."]

    fn = table.footnotes[2]
    print(fn)
    assert fn.prefix == "†)"
    assert fn.text == "Source: OECD."
    assert fn.references == ["2010†)", "2011†)"]

    fn = table.footnotes[3]
    print(fn)
    assert fn.prefix == "2"
    assert fn.text == ""
    assert fn.references == ["New Zealand 2"]

    fn = table.footnotes[4]
    print(fn)
    assert fn.prefix == "a."
    assert fn.text == "whataboutthis"
    assert fn.references == ["2011 Test  a.", "a."]

    expected = [
        ["1 Official development assistance", "", "", "", "", "", ""],
        [
            "Country",
            "Million dollar",
            "Million dollar",
            "Million dollar",
            "Percentage of GNI",
            "Percentage of GNI",
            "Percentage of GNI",
        ],
        [
            "",
            "2007",
            "2010 Test ",
            "2011 Test   whataboutthis ",
            "2007",
            "2010 Source: OECD. ",
            "2011 Source: OECD. ",
        ],
        [" whataboutthis ", "3735", "4580", "4936", "0.95", "1.1", "1"],
        ["2", "2669", "3826", "4799", "0.32", "0.32", "0.35"],
        ["New Zealand ", "320", "342", "429", "0.27", "0.26", "0.28"],
        ["OECD/DAC Footnote text.", "104206", "128465", "133526", "0.27", "0.32", "0.31"],
        ["c", "Footnote text.", "", "", "", "", ""],
        [
            "* Test",
            "This is now just a note",
            " because the footnote text was found on the left",
            "",
            "",
            "",
            "",
        ],
        ["†) Source: OECD.", "", "", "", "", "", ""],
        ["2", "", "", "", "", "", ""],
        ["a.whataboutthis", "", "", "", "", "", ""],
        [
            "0.32 This should not be recognized as a footnote",
            "This should not be recognized as a footnote.",
            "",
            "",
            "",
            "",
            "",
        ],
    ]
    assert expected == table.pre_cleaned_table.tolist()


def test_table_dont_use_footnotes():
    table = TableF(
        "./tests/data/table_example_footnotes.csv", use_footnotes=False, use_spanning_cells=False
    )
    table.print()

    fn = table.footnotes[0]
    print(fn)
    assert fn.prefix == "c"
    assert fn.text == "Footnote text."
    assert fn.references == ["OECD/DAC c"]

    fn = table.footnotes[1]
    print(fn)
    assert fn.prefix == "*"
    assert fn.text == "Test"
    assert fn.references == ["2010*", "2011* a."]

    fn = table.footnotes[2]
    print(fn)
    assert fn.prefix == "†)"
    assert fn.text == "Source: OECD."
    assert fn.references == ["2010†)", "2011†)"]

    fn = table.footnotes[3]
    print(fn)
    assert fn.prefix == "2"
    assert fn.text == ""
    assert fn.references == ["New Zealand 2"]

    fn = table.footnotes[4]
    print(fn)
    assert fn.prefix == "a."
    assert fn.text == "whataboutthis"
    assert fn.references == ["2011* a.", "a."]

    expected = [
        ["1 Official development assistance", "", "", "", "", "", ""],
        [
            "Country",
            "Million dollar",
            "Million dollar",
            "Million dollar",
            "Percentage of GNI",
            "Percentage of GNI",
            "Percentage of GNI",
        ],
        ["", "2007", "2010*", "2011* a.", "2007", "2010†)", "2011†)"],
        ["a.", "3735", "4580", "4936", "0.95", "1.1", "1"],
        ["2", "2669", "3826", "4799", "0.32", "0.32", "0.35"],
        ["New Zealand 2", "320", "342", "429", "0.27", "0.26", "0.28"],
        ["OECD/DAC c", "104206", "128465", "133526", "0.27", "0.32", "0.31"],
        ["c", "Footnote text.", "", "", "", "", ""],
        [
            "* Test",
            "This is now just a note",
            " because the footnote text was found on the left",
            "",
            "",
            "",
            "",
        ],
        ["†) Source: OECD.", "", "", "", "", "", ""],
        ["2", "", "", "", "", "", ""],
        ["a.whataboutthis", "", "", "", "", "", ""],
        [
            "0.32 This should not be recognized as a footnote",
            "This should not be recognized as a footnote.",
            "",
            "",
            "",
            "",
            "",
        ],
    ]
    assert expected == table.pre_cleaned_table.tolist()
