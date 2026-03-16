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

### Requirement: Dead function build_category_table is removed
The function `build_category_table` SHALL NOT exist anywhere in `src/chemtabextract/`. No import site references it.

#### Scenario: Function absent from codebase
- **WHEN** the `src/` tree is grepped for `build_category_table`
- **THEN** no matches are found

### Requirement: Module-level metadata constants removed from __init__.py
`__title__`, `__author__`, `__email__`, `__license__`, `__copyright__` SHALL NOT be defined in `chemtabextract/__init__.py` (these are already declared in `pyproject.toml`).

#### Scenario: No redundant constants
- **WHEN** `chemtabextract/__init__.py` is parsed
- **THEN** none of `__title__`, `__author__`, `__email__`, `__license__`, `__copyright__` are defined
