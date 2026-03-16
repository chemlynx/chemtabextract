# -*- coding: utf-8 -*-
"""
Re-exports all symbols consumed by table.py from the algorithms sub-package.

Downstream projects MUST NOT import the private sub-modules (_utils, _mips,
_structure, _categorize) directly. Import from this facade instead.
"""

from chemtabextract.table.algorithms._utils import (
    empty_string,
    empty_cells,
    standardize_empty,
    pre_clean,
    clean_unicode,
    duplicate_rows,
    duplicate_columns,
)
from chemtabextract.table.algorithms._mips import (
    find_cc4,
    find_cc1_cc2,
    find_cc3,
)
from chemtabextract.table.algorithms._structure import (
    find_title_row,
    find_note_cells,
    prefix_duplicate_labels,
    duplicate_spanning_cells,
    header_extension_up,
    header_extension_down,
)
from chemtabextract.table.algorithms._categorize import (
    categorize_header,
    split_table,
    find_row_header_table,
    clean_row_header,
)
