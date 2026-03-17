## Why

The `improvements-backlog-sweep` change (archived 2026-03-17) fixed all code
defects E1–E3, Q1–Q9, A1–A2, T1, D1 and added substantial test coverage —
overall branch coverage is now 85 %. Three test-coverage items from
IMPROVEMENTS.md remain open:

- **TC1** — `from_html.py` is now at 69 % (up from 11 %), but `read_url()` and
  `configure_selenium()` remain uncovered because they require network / Selenium.
- **TC2** — Several behaviours listed as untested in the backlog still have no
  tests: `CellParser.replace()`, `StringParser.cut()`, `Table.contains()`,
  `print_category_table()`, the `use_max_data_area=True` code path, the
  mid-list subtable `continue` path, and `TrivialTable.col_header` /
  `row_header` with degenerate table sizes.
- **TC3** — `conftest.py` defines 13 fixtures (`table_example1`–`table_example13`)
  but no test function receives any of them via pytest injection; they are dead
  code.

TC4 is already resolved: `fail_under` was raised to 75 in the sweep.

## What Changes

- **TC1** — Add mocked tests for `read_url()` (requests path and Selenium
  fallback) and `configure_selenium()` in `tests/test_input_from_html.py`.
- **TC2** — Add targeted unit tests for the behaviours listed above, distributed
  across `tests/test_table_parse.py`, `tests/test_table_table.py`, and
  `tests/test_trivial_table.py`.
- **TC3** — Wire `conftest.py` fixtures into matching existing tests (replacing
  inline `Table(...)` construction), or remove fixtures that cannot be usefully
  injected. Add docstrings to `table_example2`–`table_example13`.

## Capabilities

### New Capabilities

_(none — no new production capabilities)_

### Modified Capabilities

- `pytest-suite`: TC1 `read_url`/`configure_selenium` mock tests added;
  TC2 targeted unit tests added; TC3 fixtures wired or culled.

## Impact

- **`tests/test_input_from_html.py`** — new TC1 mock tests for `read_url` /
  `configure_selenium`
- **`tests/test_table_parse.py`** — TC2 tests for `CellParser.replace`,
  `StringParser.cut`
- **`tests/test_table_table.py`** — TC2 tests for `Table.contains`,
  `use_max_data_area=True`, mid-list subtable continue path
- **`tests/test_trivial_table.py`** — TC2 tests for `TrivialTable.col_header` /
  `row_header` degenerate sizes
- **`tests/test_output_to_pandas.py`** (new) — TC2 test for
  `print_category_table`
- **`tests/conftest.py`** — TC3 fixture wiring or orphan removal
- No production code changes in this change
