## Context

This change is test-only: no production code changes are planned. The codebase
is at 85 % overall branch coverage after the sweep. Three categories of gaps
remain (TC1, TC2, TC3). The main decisions concern mocking strategy for
network-dependent code (TC1) and the disposition of orphaned fixtures (TC3).

## Goals / Non-Goals

**Goals:**
- Cover `read_url()` and `configure_selenium()` in `from_html.py` via mocks,
  bringing `from_html.py` from 69 % to ≥ 85 % branch coverage.
- Add targeted unit tests for the specific untested behaviours in TC2.
- Resolve TC3 by wiring fixtures or removing dead ones.
- Keep the test suite fast: no new tests should require network access or a
  browser.

**Non-Goals:**
- Integration tests that actually fetch real URLs (those belong in a separate,
  optional test tier marked `@pytest.mark.integration`).
- Increasing overall coverage above 90 % — the remaining gaps are mostly in
  the Selenium / MIPS edge-case paths and are not worth the maintenance cost.
- Changing any production code to make it more testable (a separate refactor
  concern).

## Decisions

### Decision 1: Mock `requests` and `selenium` at the module-import boundary

**Options considered:**

A. Patch `requests.get` with `unittest.mock.patch` inside each test.
B. Use `pytest-httpserver` or `responses` library to intercept HTTP calls.
C. Monkeypatch the module-level `requests` import in `from_html`.

**Decision: Option A** — `unittest.mock.patch("chemtabextract.input.from_html.requests.get")`
and `patch("chemtabextract.input.from_html.configure_selenium")`. This avoids
new test dependencies and is the standard pattern in the project. The patched
`requests.get` returns a `MagicMock` with a `.text` attribute holding a
hand-crafted HTML snippet. The Selenium fallback is tested by making `requests.get`
raise `requests.exceptions.ConnectionError` and patching `configure_selenium`
to return a mock driver whose `.page_source` attribute holds the same HTML.

### Decision 2: TC3 fixture disposition — wire, not remove

The 13 fixtures in `conftest.py` cover the full range of table examples used by
integration tests. Rather than removing them, the preferred approach is:

1. Replace the inline `Table("./tests/data/table_exampleN.csv")` construction in
   existing tests with fixture injection wherever the match is straightforward
   (i.e., the test uses exactly that file with default construction).
2. For fixtures where no existing test uses that exact file, add a minimal smoke
   test (`test_<fixture>_loads_without_error`) inside a new
   `tests/test_conftest_fixtures.py` so each fixture is exercised at least once.
3. Add docstrings to `table_example2`–`table_example13` describing the table
   structure (as required by the project conventions).

This preserves the fixtures as reusable infrastructure for future tests.

### Decision 3: TC2 test placement

| Behaviour | Target file |
|---|---|
| `CellParser.replace()` | `tests/test_table_parse.py` (already has `TestCellParserCut` class) |
| `StringParser.cut()` | `tests/test_table_parse.py` |
| `Table.contains()` | `tests/test_table_table.py` |
| `use_max_data_area=True` path | `tests/test_table_table.py` |
| mid-list subtable `continue` path | `tests/test_table_table_subtables.py` |
| `TrivialTable.col_header`/`row_header` degenerate | `tests/test_trivial_table.py` |
| `print_category_table()` | new `tests/test_output_to_pandas.py` |

### Decision 4: HTML fixture for TC1 mock tests

Use an inline HTML string (not a file fixture) for the `requests.get` mock. This
keeps the test self-contained and avoids proliferating small fixture files. If
the HTML string grows unwieldy, move it to `tests/data/simple_table.html`.
The HTML should include a 2×3 table with a `colspan` and a `rowspan` cell so the
mock tests also exercise the cell-filling logic.

## Risks / Trade-offs

- **Mocking tightly couples tests to internal module structure**: patching
  `chemtabextract.input.from_html.requests.get` means tests will break if the
  import is refactored. Acceptable trade-off given the project scale.
  → Mitigation: document the patch target in the test docstring.

- **Orphaned fixtures that are structurally different**: some `table_example`
  files may not map cleanly to existing test assertions. The smoke-test approach
  (Decision 3, step 2) intentionally accepts shallow coverage for these to avoid
  forcing artificial assertions.
  → Mitigation: fixture docstrings will describe the table so future contributors
  know when to use each fixture.

- **`print_category_table()` is a side-effect function** (prints to stdout): tests
  must use `capsys` or `capfd` to assert on its output. The function currently
  has no return value.
  → Mitigation: use `capsys.readouterr()` pattern; assert that output contains
  expected column headers and row values.
