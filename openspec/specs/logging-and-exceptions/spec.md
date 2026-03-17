## ADDED Requirements

### Requirement: Library does not configure root logging
`chemtabextract/__init__.py` SHALL install a `NullHandler` on the package logger and SHALL NOT call `logging.basicConfig()`, create any `FileHandler`, or write any log file. No `tde_log.txt` file SHALL be created at import time or during normal use.

#### Scenario: No log file created on import
- **WHEN** `import chemtabextract` is executed in a clean working directory
- **THEN** no `tde_log.txt` or other log file is created in the working directory

#### Scenario: NullHandler installed
- **WHEN** the `chemtabextract` package logger is inspected after import
- **THEN** it has exactly one handler of type `logging.NullHandler`

#### Scenario: Root logger not polluted
- **WHEN** `chemtabextract` is imported
- **THEN** the root logger's handler list is unchanged

### Requirement: All public exceptions importable from top-level namespace
`TDEError`, `InputError`, and `MIPSError` SHALL be importable directly from `chemtabextract` (i.e., `from chemtabextract import TDEError`). They SHALL also remain importable from `chemtabextract.exceptions`.

#### Scenario: Top-level exception imports succeed
- **WHEN** `from chemtabextract import TDEError, InputError, MIPSError` is executed
- **THEN** all three symbols are available

#### Scenario: Exception hierarchy preserved
- **WHEN** exception classes are inspected
- **THEN** `InputError` is a subclass of `TDEError` and `MIPSError` is a subclass of `TDEError`

#### Scenario: Direct module import still works
- **WHEN** `from chemtabextract.exceptions import TDEError` is executed
- **THEN** the symbol is available

### Requirement: Dead function build_category_table removed from algorithms.py
The dead `build_category_table` function that existed in `src/chemtabextract/table/algorithms/` SHALL be removed. Note: a separate, live `build_category_table` function in `src/chemtabextract/output/to_pandas.py` is used by `table.py` and SHALL be retained.

#### Scenario: Dead copy absent from algorithms module
- **WHEN** `src/chemtabextract/table/algorithms/` is grepped for `build_category_table`
- **THEN** no matches are found

### Requirement: Module-level metadata constants removed from __init__.py
`__title__`, `__author__`, `__email__`, `__license__`, `__copyright__` SHALL NOT be defined in `chemtabextract/__init__.py` (these are already declared in `pyproject.toml`).

#### Scenario: No redundant constants
- **WHEN** `chemtabextract/__init__.py` is parsed
- **THEN** none of `__title__`, `__author__`, `__email__`, `__license__`, `__copyright__` are defined

### Requirement: TypeError in create_table carries a single clean message string
`create_table()` in `input/from_any.py` SHALL raise `TypeError` with a single
string argument that includes both the explanation and the invalid input value.
The form `raise TypeError(msg, str(name_key))` (two positional args) SHALL NOT
be used.

#### Scenario: TypeError message is a clean string
- **WHEN** `create_table("")` is called with an unsupported input
- **THEN** `str(err)` on the caught `TypeError` equals a single descriptive
  string (not a repr of a tuple)

### Requirement: Truncation warning emitted when cell values exceed 200 characters
Input parsers (`from_csv`, `from_html`, `from_list`) SHALL emit a
`logging.warning` if any cell value in the parsed table exceeds 200 characters,
indicating that data may have been truncated.

#### Scenario: Warning emitted for long cells
- **WHEN** a CSV, HTML, or list input contains a cell with more than 200
  characters
- **THEN** a warning is logged mentioning the cell length or truncation risk

#### Scenario: No warning for normal-length cells
- **WHEN** all cell values are 200 characters or fewer
- **THEN** no truncation warning is logged

### Requirement: Input parsers use dynamic numpy dtype
`from_csv.read()`, `from_html.makearray()`, and `from_list.read()` SHALL
derive the numpy array dtype from the maximum cell length in the input data.
The fixed `dtype="<U60"` SHALL NOT be used. The derived dtype SHALL be at least
`<U1`.

#### Scenario: Cell values are not truncated
- **WHEN** a table contains a cell value of 100 characters
- **THEN** the numpy array stores all 100 characters without truncation
