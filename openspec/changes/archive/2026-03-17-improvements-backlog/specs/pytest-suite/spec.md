## MODIFIED Requirements

### Requirement: Coverage baseline recorded at ≥40%
`pytest-cov` SHALL be configured in `pyproject.toml` with `fail_under = 75`
(already in place). This requirement is updated to reflect the raised floor.

#### Scenario: Coverage gate passes
- **WHEN** `uv run pytest --cov=chemtabextract` is run
- **THEN** the command exits 0 and total branch coverage is reported as ≥ 75 %

#### Scenario: Coverage config in pyproject.toml
- **WHEN** `pyproject.toml` is parsed
- **THEN** `[tool.coverage.report]` contains `fail_under = 75`

## ADDED Requirements

### Requirement: read_url and configure_selenium are covered by mock tests
`tests/test_input_from_html.py` SHALL contain tests for `read_url()` and
`configure_selenium()` that use `unittest.mock.patch` to avoid real network
calls. No test SHALL require a live internet connection or a Selenium browser.

#### Scenario: read_url happy path via requests mock
- **WHEN** `requests.get` is patched to return a response whose `.text` is a
  valid HTML page with one table
- **THEN** `read_url(url)` returns a numpy array whose shape matches the table

#### Scenario: read_url raises TypeError for non-integer table_number
- **WHEN** `read_url("http://example.com", table_number="1")` is called
- **THEN** `TypeError` is raised

#### Scenario: read_url raises InputError for out-of-range table_number
- **WHEN** `requests.get` is patched to return a page with one table and
  `read_url(url, table_number=99)` is called
- **THEN** `InputError` is raised

#### Scenario: read_url falls back to Selenium when requests raises ConnectionError
- **WHEN** `requests.get` is patched to raise `requests.exceptions.ConnectionError`
  and `configure_selenium` is patched to return a mock driver whose `.page_source`
  contains a valid HTML table
- **THEN** `read_url(url)` returns a numpy array without raising

#### Scenario: read_url raises InputError when requests fails and selenium unavailable
- **WHEN** `requests.get` is patched to raise `requests.exceptions.ConnectionError`
  and `_SELENIUM_AVAILABLE` is patched to `False`
- **THEN** `InputError` is raised with a message mentioning the optional web extra

#### Scenario: configure_selenium returns Firefox driver by default
- **WHEN** `webdriver.Firefox` is patched and `configure_selenium()` is called
  with default arguments
- **THEN** the patched `webdriver.Firefox` is called once and its return value
  is returned

#### Scenario: configure_selenium returns None for unknown browser
- **WHEN** `configure_selenium(browser="Chrome")` is called (no Chrome support
  in the current implementation)
- **THEN** `None` is returned

### Requirement: CellParser.replace is covered by unit tests
`tests/test_table_parse.py` SHALL contain a `TestCellParserReplace` class with
tests for `CellParser.replace()`.

#### Scenario: replace substitutes matched pattern in matching cells
- **WHEN** `CellParser(r"\d+").replace(array, "NUM")` is called on a 2-D array
  containing cells with digits
- **THEN** matched cells have their digits replaced by `"NUM"` in the returned array

#### Scenario: replace does not modify non-matching cells
- **WHEN** `CellParser(r"\d+").replace(array, "NUM")` is called
- **THEN** cells that do not match the pattern are unchanged in the result

### Requirement: StringParser.cut is covered by unit tests
`tests/test_table_parse.py` SHALL contain a `TestStringParserCut` class with
tests for `StringParser.cut()`.

#### Scenario: StringParser.cut returns expected substrings for matched cells
- **WHEN** `StringParser(r"(\w+)=(\w+)").cut(array)` is called on a 2-D array
  containing `"key=value"` cells
- **THEN** the generator yields tuples containing the row index, column index,
  captured groups, and residual string

### Requirement: Table.contains is covered by unit tests
`tests/test_table_table.py` SHALL contain tests for `Table.contains()`.

#### Scenario: contains returns True when a cell matches the query
- **WHEN** `table.contains("some value")` is called and the table has a cell
  with that value
- **THEN** `True` is returned

#### Scenario: contains returns False when no cell matches
- **WHEN** `table.contains("nonexistent value")` is called
- **THEN** `False` is returned

### Requirement: use_max_data_area=True code path is covered by unit tests
`tests/test_table_table.py` SHALL contain at least one test that constructs a
`Table` with `use_max_data_area=True` and verifies the analysis runs without error.

#### Scenario: Table analyses successfully with use_max_data_area=True
- **WHEN** `Table("./tests/data/table_example1.csv", use_max_data_area=True)` is
  constructed
- **THEN** no exception is raised and `table.category_table` is not `None`

### Requirement: Mid-list subtable continue path is covered
`tests/test_table_table_subtables.py` SHALL contain a test that verifies the
`continue` path when a mid-list subtable fails MIPS analysis: the remaining
subtables are still returned (the failure does not abort the list).

#### Scenario: Failing subtable does not prevent later subtables from being returned
- **WHEN** a table's structure causes the second of three subtables to fail MIPS
- **THEN** the returned subtable list contains the first and third subtables
  (or at minimum, the failure does not raise an unhandled exception)

### Requirement: TrivialTable.col_header and row_header are tested with degenerate sizes
`tests/test_trivial_table.py` SHALL contain tests for `TrivialTable.col_header`
and `TrivialTable.row_header` on tables that are smaller than the header
extraction expects (e.g., a 1×1 or 1×2 table).

#### Scenario: TrivialTable.col_header on a single-row table returns None
- **WHEN** `TrivialTable` is constructed from a CSV with exactly one row
- **THEN** `table.col_header` returns `None` without raising

#### Scenario: TrivialTable.row_header on a single-column table returns None
- **WHEN** `TrivialTable` is constructed from a CSV with exactly one column
- **THEN** `table.row_header` returns `None` without raising

### Requirement: print_category_table is covered by unit tests
`tests/test_output_to_pandas.py` SHALL contain tests for `print_category_table()`.

#### Scenario: print_category_table writes column headers to stdout
- **WHEN** `print_category_table(table)` is called with a `Table` that has
  category data
- **THEN** the captured stdout contains column header text from the table

#### Scenario: print_category_table does not raise for a table with no categories
- **WHEN** `print_category_table(table)` is called with a minimal table
- **THEN** no exception is raised

### Requirement: conftest.py fixtures are injected by at least one test each
Every fixture defined in `tests/conftest.py` SHALL be used as a pytest-injected
parameter by at least one test function. Fixtures for which no meaningful
assertion can be made SHALL be covered by a smoke test that simply asserts the
fixture object is not `None`.

#### Scenario: All conftest fixtures are exercised
- **WHEN** `uv run pytest tests/` is run
- **THEN** pytest reports zero "unused fixture" warnings for fixtures defined in
  `conftest.py` (verified by `--co -q` showing each fixture is referenced)

### Requirement: conftest.py fixtures have docstrings
All fixture functions in `tests/conftest.py` SHALL have Google-style docstrings
describing the table structure (number of rows/columns, notable features such
as spanning cells or footnotes).

#### Scenario: All fixtures documented
- **WHEN** `tests/conftest.py` source is inspected
- **THEN** every `@pytest.fixture` function has a non-empty docstring
