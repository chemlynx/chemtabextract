"""
Re-exports all symbols consumed by table.py from the algorithms sub-package.

Downstream projects MUST NOT import the private sub-modules (_utils, _mips,
_structure, _categorize) directly. Import from this facade instead.
"""

from chemtabextract.table.algorithms._categorize import (
    clean_row_header,  # noqa: F401
    find_row_header_table,  # noqa: F401
    split_table,  # noqa: F401
)
from chemtabextract.table.algorithms._mips import (
    find_cc1_cc2,  # noqa: F401
    find_cc3,  # noqa: F401
    find_cc4,  # noqa: F401
)
from chemtabextract.table.algorithms._structure import (
    duplicate_spanning_cells,  # noqa: F401
    find_note_cells,  # noqa: F401
    find_title_row,  # noqa: F401
    header_extension_down,  # noqa: F401
    header_extension_up,  # noqa: F401
    prefix_duplicate_labels,  # noqa: F401
)
from chemtabextract.table.algorithms._utils import (
    clean_unicode,  # noqa: F401
    duplicate_columns,  # noqa: F401
    duplicate_rows,  # noqa: F401
    empty_cells,  # noqa: F401
    empty_string,  # noqa: F401
    pre_clean,  # noqa: F401
    standardize_empty,  # noqa: F401
)
