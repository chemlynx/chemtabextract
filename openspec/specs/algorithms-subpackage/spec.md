## ADDED Requirements

### Requirement: algorithms.py is replaced by an algorithms/ sub-package
The file `src/chemtabextract/table/algorithms.py` SHALL NOT exist. In its place, a `src/chemtabextract/table/algorithms/` directory SHALL contain an `__init__.py` and four internal sub-modules: `_utils.py`, `_mips.py`, `_structure.py`, `_categorize.py`.

#### Scenario: Original file absent
- **WHEN** the repository is listed
- **THEN** `src/chemtabextract/table/algorithms.py` does not exist

#### Scenario: Sub-package directory present
- **WHEN** the repository is listed
- **THEN** `src/chemtabextract/table/algorithms/__init__.py` exists

### Requirement: _utils.py contains utility functions
`_utils.py` SHALL contain: `empty_string`, `empty_cells`, `standardize_empty`, `pre_clean`, `clean_unicode`, `duplicate_rows`, `duplicate_columns`. Logic SHALL be identical to the originals in `algorithms.py`.

#### Scenario: Utility functions importable
- **WHEN** `from chemtabextract.table.algorithms._utils import empty_string, pre_clean` is executed
- **THEN** both symbols are available

### Requirement: _mips.py contains MIPS core functions with zero logic changes
`_mips.py` SHALL contain: `find_cc4`, `find_cc1_cc2`, `find_cc3`. The function bodies SHALL be verbatim copies from the original `algorithms.py` — no formatting changes, no renames, no logic alterations.

#### Scenario: MIPS functions importable
- **WHEN** `from chemtabextract.table.algorithms._mips import find_cc4, find_cc1_cc2, find_cc3` is executed
- **THEN** all three symbols are available

#### Scenario: MIPS logic unchanged
- **WHEN** the full test suite is run after the split
- **THEN** all tests pass with identical results to pre-split behaviour

### Requirement: _structure.py contains header and structure functions
`_structure.py` SHALL contain: `find_title_row`, `find_note_cells`, `prefix_duplicate_labels`, `duplicate_spanning_cells`, `header_extension_up`, `header_extension_down`. Logic SHALL be identical to originals.

#### Scenario: Structure functions importable
- **WHEN** `from chemtabextract.table.algorithms._structure import find_title_row, header_extension_up` is executed
- **THEN** both symbols are available

### Requirement: _categorize.py contains categorisation functions
`_categorize.py` SHALL contain: `categorize_header`, `split_table`, `find_row_header_table`, `clean_row_header`. Logic SHALL be identical to originals.

#### Scenario: Categorisation functions importable
- **WHEN** `from chemtabextract.table.algorithms._categorize import categorize_header, split_table` is executed
- **THEN** both symbols are available

### Requirement: algorithms/__init__.py re-exports all symbols consumed by table.py
`algorithms/__init__.py` SHALL re-export every symbol that `table.py` imports from `algorithms`, so that `table.py` requires no changes.

#### Scenario: Facade re-exports all expected symbols
- **WHEN** `from chemtabextract.table.algorithms import (empty_string, find_cc4, find_title_row, categorize_header)` is executed
- **THEN** all symbols are available

#### Scenario: table.py unchanged
- **WHEN** the import line in table.py is inspected
- **THEN** it imports from `chemtabextract.table.algorithms` (the facade) without modification

### Requirement: Full test suite passes after the split
All tests that passed before the `algorithms.py` split SHALL continue to pass after it. This is the primary regression guard.

#### Scenario: Test suite green after split
- **WHEN** `uv run pytest tests/` is run after the split
- **THEN** all tests pass with no failures or errors
