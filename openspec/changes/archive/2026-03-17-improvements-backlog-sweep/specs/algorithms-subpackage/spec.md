## MODIFIED Requirements

### Requirement: _categorize.py contains categorisation functions
`_categorize.py` SHALL contain: `split_table`, `find_row_header_table`,
`clean_row_header`. The function `categorize_header` SHALL NOT be present.
The `sympy` import SHALL NOT be present.

#### Scenario: Categorisation functions importable
- **WHEN** `from chemtabextract.table.algorithms._categorize import split_table` is executed
- **THEN** the symbol is available

#### Scenario: categorize_header absent
- **WHEN** `_categorize.py` is inspected
- **THEN** no function named `categorize_header` exists

### Requirement: algorithms/__init__.py re-exports all symbols consumed by table.py
`algorithms/__init__.py` SHALL re-export every symbol that `table.py` imports
from `algorithms`. `categorize_header` SHALL NOT be re-exported.

#### Scenario: Facade re-exports expected symbols
- **WHEN** `from chemtabextract.table.algorithms import (empty_string, find_cc4, find_title_row)` is executed
- **THEN** all symbols are available

#### Scenario: categorize_header not in facade
- **WHEN** `from chemtabextract.table.algorithms import categorize_header` is executed
- **THEN** `ImportError` is raised

## ADDED Requirements

### Requirement: prefixed_row_or_column result is cached per call-site
Each call-site in `prefix_duplicate_labels` that checks and then unpacks the
result of `prefixed_row_or_column` SHALL assign the result once and test the
cached value, avoiding a second full O(n×m) scan.

#### Scenario: No double call
- **WHEN** `_structure.py` source is inspected at the column-header prefixing
  block
- **THEN** `prefixed_row_or_column(array)` appears at most once per logical
  branch (assign once, then test)

### Requirement: Table provides a config-override context manager
`Table` SHALL provide a `_override_config(key: str, value: object)` context
manager. While the context is active, `self._configs[key]` SHALL equal `value`.
On exit (including exception paths), `self._configs[key]` SHALL be restored to
its original value. External code that needs to temporarily change a config
SHALL use this context manager.

#### Scenario: Config is restored after context exits normally
- **WHEN** `table._override_config("use_title_row", False)` is entered and then
  exited normally
- **THEN** `table.configs["use_title_row"]` equals its original value

#### Scenario: Config is restored after exception inside context
- **WHEN** an exception is raised inside `table._override_config(...)` block
- **THEN** `table.configs["use_title_row"]` is restored before the exception
  propagates

### Requirement: Table.configs returns a copy
The public `Table.configs` property SHALL return a copy of `self._configs`, so
that callers cannot mutate the live configuration dict.

#### Scenario: Mutating the returned dict does not affect Table state
- **WHEN** `cfg = table.configs; cfg["use_title_row"] = False` is executed
- **THEN** `table.configs["use_title_row"]` is unchanged

### Requirement: CellParser.cut raises ValueError on 1-D input
`CellParser.cut()` SHALL raise `ValueError` with a clear message if the
supplied `table` array has `ndim != 2`.

#### Scenario: 1-D array raises ValueError
- **WHEN** `CellParser("x").cut(np.array(["a", "b"]))` is called
- **THEN** `ValueError` is raised with a message indicating 2-D input is required

### Requirement: _cc4 and _cc3 are computed once after _analyze_table completes
After `_analyze_table()` finishes in `Table`, the results of `_cc4` and `_cc3`
SHALL be cached as instance attributes. Subsequent property accesses SHALL
return the cached values without re-running `find_cc4` or `find_cc3`. The
cache SHALL be cleared at the start of each new `_analyze_table()` call.

#### Scenario: Cache cleared on re-analysis
- **WHEN** `table.transpose()` is called (which triggers `_analyze_table` again)
- **THEN** `_cc4` and `_cc3` are recomputed from scratch

### Requirement: _analyze_table documents its ordering constraints
`Table._analyze_table` SHALL contain inline comments at each step explaining
what prior state is required. At minimum, the three ordering constraints from
A2 in IMPROVEMENTS.md SHALL be documented.

#### Scenario: Comments present
- **WHEN** `Table._analyze_table` source is inspected
- **THEN** comments describe the prerequisite state for `_cc4` first access,
  `duplicate_spanning_cells`, and `_cc3` access
