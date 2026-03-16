## ADDED Requirements

### Requirement: No unittest.TestCase classes remain in tests/
All test files in `tests/` SHALL use native pytest style (top-level `def test_*()` functions). No `unittest.TestCase` subclasses, no `import unittest`, no `self.assert*` calls, no `unittest.main()` calls SHALL remain.

#### Scenario: No unittest imports
- **WHEN** the `tests/` tree is grepped for `import unittest`
- **THEN** no matches are found

#### Scenario: No TestCase subclasses
- **WHEN** the `tests/` tree is grepped for `unittest.TestCase`
- **THEN** no matches are found

### Requirement: Shared fixtures defined in tests/conftest.py
`tests/conftest.py` SHALL define shared `pytest.fixture` functions for commonly reused `Table` instances. At minimum, a `table_example1` fixture returning `Table('./tests/data/table_example1.csv')` SHALL be present.

#### Scenario: conftest.py exists
- **WHEN** the `tests/` directory is listed
- **THEN** `conftest.py` exists

#### Scenario: table_example1 fixture available
- **WHEN** a test function declares `table_example1` as a parameter
- **THEN** pytest injects a `Table` instance constructed from `table_example1.csv`

### Requirement: All eleven test files migrated
The following test files SHALL be migrated to native pytest:
`test_input_from_csv.py`, `test_output_from_csv.py`, `test_trivial_table.py`,
`test_table_footnotes.py`, `test_row_categories.py`,
`test_table_table_spanning_cells.py`, `test_table_table_header_extension.py`,
`test_table_table_header_extens_d.py`, `test_table_table_subtables.py`,
`test_table_table.py`, `test_tde.py`.

#### Scenario: All test files pass after migration
- **WHEN** `uv run pytest tests/` is run after all migrations
- **THEN** all tests pass with no failures

### Requirement: Coverage baseline recorded at ≥40%
After migration, `pytest-cov` SHALL be configured in `pyproject.toml` with `fail_under = 40` (or higher, based on the measured baseline). The measured percentage SHALL be recorded as the floor.

#### Scenario: Coverage gate passes
- **WHEN** `uv run pytest --cov=chemtabextract --cov-fail-under=40` is run
- **THEN** the command exits 0

#### Scenario: Coverage config in pyproject.toml
- **WHEN** `pyproject.toml` is parsed
- **THEN** `[tool.coverage.report]` contains `fail_under` set to the measured baseline value

### Requirement: New tests test_url_validation.py and test_public_interface.py exist
`tests/test_url_validation.py` SHALL contain parametrised tests for the `url()` function covering all cases in the dependency-management spec. `tests/test_public_interface.py` SHALL verify top-level imports and confirm no log file is created on import.

#### Scenario: URL validation tests present and pass
- **WHEN** `pytest tests/test_url_validation.py` is run
- **THEN** all parametrised cases pass

#### Scenario: Public interface tests present and pass
- **WHEN** `pytest tests/test_public_interface.py` is run
- **THEN** all tests pass including the no-log-file assertion
