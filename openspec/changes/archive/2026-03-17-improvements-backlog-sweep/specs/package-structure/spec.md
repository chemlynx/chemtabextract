## MODIFIED Requirements

### Requirement: pyproject.toml declares correct metadata
`pyproject.toml` SHALL declare `name = "chemtabextract"`,
`requires-python = ">=3.13"`, and a `[tool.commitizen]` section with
`version_provider = "pep621"`. The `pandas` dependency SHALL be declared as
`pandas>=0.25`.

#### Scenario: Package name
- **WHEN** `pyproject.toml` is parsed
- **THEN** `project.name` equals `"chemtabextract"`

#### Scenario: Commitizen config present
- **WHEN** `pyproject.toml` is parsed
- **THEN** a `[tool.commitizen]` section exists with `version_provider = "pep621"`

#### Scenario: pandas floor is 0.25
- **WHEN** `pyproject.toml` is parsed
- **THEN** the pandas dependency specifier is `>=0.25` (or higher)

## REMOVED Requirements

### Requirement: sympy is a runtime dependency
**Reason:** `sympy` was only used by `categorize_header`, which is being removed
as it is unused and untested (see Q8 in IMPROVEMENTS.md).
**Migration:** No migration path; `categorize_header` had no documented public
use. Remove any downstream code that called it.

## ADDED Requirements

### Requirement: Dead pandas MultiIndex.labels compatibility code is absent
`output/to_pandas.py` SHALL NOT contain any `hasattr(df.index, "labels")` or
`hasattr(df.columns, "labels")` branch. Only the `codes` path (pandas ≥ 0.24)
and the flat-index fallback SHALL remain.

#### Scenario: labels branch absent
- **WHEN** `output/to_pandas.py` is grepped for `"labels"`
- **THEN** no matches are found

### Requirement: list_as_PrettyTable is renamed to list_as_pretty_table
The function `list_as_PrettyTable` in `output/print.py` SHALL be renamed to
`list_as_pretty_table`. All call-sites (currently `table.py`) SHALL use the new
name.

#### Scenario: Old name absent
- **WHEN** the source tree is grepped for `list_as_PrettyTable`
- **THEN** no matches are found

#### Scenario: New name importable
- **WHEN** `from chemtabextract.output.print import list_as_pretty_table` is executed
- **THEN** the symbol is available

### Requirement: makearray fills corner cells for combined colspan+rowspan
When an HTML table cell has both `colspan` and `rowspan` attributes,
`makearray()` SHALL fill all intersection cells `(row+r, col+c)` for
`r in range(1, rowspan)` and `c in range(1, colspan)`.

#### Scenario: Corner cells populated
- **WHEN** an HTML table has a cell with `rowspan=2 colspan=2`
- **THEN** all four covered positions in the numpy array contain the cell's text

### Requirement: Pointless try/except/raise in _analyze_table is removed
`Table._analyze_table` SHALL NOT contain a `try/except MIPSError: raise` block
that only re-raises the exception. The code accessing `self._cc3` SHALL allow
`MIPSError` to propagate naturally.

#### Scenario: Passthrough block absent
- **WHEN** `table.py` is inspected
- **THEN** there is no `try: _ = self._cc3` / `except MIPSError: raise` block

### Requirement: _set_configs accesses _default_configs once
`Table._set_configs` SHALL assign `self._default_configs` to a local variable
once and use that variable for both the initial copy and the membership test.
The property SHALL NOT be accessed more than once per `_set_configs` call.

#### Scenario: Single property access
- **WHEN** `_set_configs` source is inspected
- **THEN** `self._default_configs` appears exactly once in the method body
