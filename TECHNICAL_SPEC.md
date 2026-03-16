# Technical Specification — chemtabextract

> **Status:** Draft v0.1 — produced by Solutions Architect session, 2026-03-16
> **Replaces:** `tabledataextractor` 1.5.11 (upstream fork; no further upstream sync)
> **Primary consumer:** ChemDataExtractor 2 (CDE2), Cambridge Molecular Engineering

---

## 1. Project Overview

`chemtabextract` is a Python library that extracts and standardises structured
data from scientific tables using the MIPS (*Minimum Indexing Point Search*)
algorithm (Embley et al., DOI: 10.1007/s10032-016-0259-1). It accepts tables
as Python lists, CSV files, HTML files, or URLs, and returns a normalised
*category table* in which every data cell is paired with its full row- and
column-header path.

The library is designed for consumption by other projects. Its primary
downstream consumer is **CDE2**, which calls `Table` and `TrivialTable`
directly. It is intended to be declared as a `pyproject.toml` dependency and
installed via `uv`.

This document describes the system as it will exist after the current
iteration of work is complete.

---

## 2. Current State Summary

The project is a maintained fork of `tabledataextractor` 1.5.11. The
algorithmic core and all public API behaviour are **frozen** — this iteration
is a modernisation and repackaging effort, not a feature change.

| Area | Action |
|---|---|
| Package name | Renamed `tabledataextractor` → `chemtabextract` |
| Package layout | Migrated to `src/` layout (`src/chemtabextract/`) |
| Build system | `setup.py` removed; `pyproject.toml` + `uv` is the sole build system |
| Django dependency | Removed; URL validation replaced with `urllib.parse` (stdlib) |
| `selenium` dependency | Demoted from runtime to optional extra (`[web]`) |
| Doc/tooling dependencies | Moved from runtime to `[dependency-groups] docs` |
| Logging anti-pattern | `FileHandler` / `basicConfig` removed; `NullHandler` installed |
| `algorithms.py` monolith | Split into four focused internal sub-modules |
| Dead code | `build_category_table` in `algorithms.py` removed |
| Test suite | Migrated from `unittest.TestCase` to native `pytest` style |
| Pre-commit quality gate | Full stack installed (ruff, mypy, bandit, vulture, xenon, pytest-cov) |
| MIPS algorithm logic | **Untouched** — no semantic changes permitted |
| Public API | **Untouched** — identical behaviour to `tabledataextractor` 1.5.11 |

---

## 3. Architecture

### 3.1 Package Structure

```
src/
└── chemtabextract/
    ├── __init__.py              # PUBLIC: exports Table, TrivialTable,
    │                            #         TDEError, InputError, MIPSError
    ├── exceptions.py            # PUBLIC: TDEError, InputError, MIPSError
    ├── input/
    │   ├── __init__.py
    │   ├── from_any.py          # internal: input dispatch; urllib.parse URL validation
    │   ├── from_csv.py          # internal
    │   ├── from_html.py         # internal: requests primary; selenium optional fallback
    │   └── from_list.py         # internal
    ├── output/
    │   ├── __init__.py
    │   ├── print.py             # internal
    │   ├── to_csv.py            # internal
    │   └── to_pandas.py         # internal
    └── table/
        ├── __init__.py
        ├── table.py             # PUBLIC (via __init__): Table, TrivialTable
        ├── footnotes.py         # internal
        ├── history.py           # internal
        ├── parse.py             # internal
        └── algorithms/          # internal sub-package
            ├── __init__.py      # re-exports all symbols consumed by table.py
            ├── _utils.py        # empty_string, empty_cells, standardize_empty,
            │                    # pre_clean, clean_unicode, duplicate_rows,
            │                    # duplicate_columns
            ├── _mips.py         # find_cc4, find_cc1_cc2, find_cc3
            │                    # *** NO LOGIC CHANGES PERMITTED ***
            ├── _structure.py    # find_title_row, find_note_cells,
            │                    # prefix_duplicate_labels, duplicate_spanning_cells,
            │                    # header_extension_up, header_extension_down
            └── _categorize.py   # categorize_header, split_table,
                                 # find_row_header_table, clean_row_header

tests/
├── conftest.py                  # shared pytest fixtures
├── data/                        # existing test data files (unchanged)
├── test_input_from_csv.py
├── test_output_from_csv.py
├── test_row_categories.py
├── test_table_footnotes.py
├── test_table_table.py
├── test_table_table_header_extens_d.py
├── test_table_table_header_extension.py
├── test_table_table_spanning_cells.py
├── test_table_table_subtables.py
├── test_tde.py
├── test_trivial_table.py
├── test_url_validation.py       # NEW: URL validation regression tests
└── test_public_interface.py     # NEW: import smoke + public surface test
```

**Public vs internal convention:**
- Public: exported from `src/chemtabextract/__init__.py`
- Internal sub-modules in `algorithms/` are prefixed `_` — downstream
  projects MUST NOT import from them directly
- All other sub-modules are internal by convention (not prefixed, but not
  re-exported at the top level)

### 3.2 Component Diagram

```
╔══════════════════════════════════════════════════════════════╗
║  Downstream consumer (e.g. CDE2)                             ║
║                                                              ║
║  from chemtabextract import Table, TrivialTable, MIPSError   ║
╚══════════════════════╦═══════════════════════════════════════╝
                       │ public API
╔══════════════════════▼═══════════════════════════════════════╗
║  chemtabextract.__init__                                     ║
║  (Table, TrivialTable, TDEError, InputError, MIPSError)      ║
╚══════╦═══════════════╦═══════════════════════════╦═══════════╝
       │               │                           │
╔══════▼═════╗  ╔══════▼══════════╗  ╔════════════▼══════════╗
║   input/   ║  ║  table/table.py ║  ║       output/         ║
║            ║  ║                 ║  ║                       ║
║ from_any   ║  ║  Table          ║  ║ to_pandas             ║
║ from_csv   ║  ║  TrivialTable   ║  ║ to_csv                ║
║ from_html  ║  ║                 ║  ║ print                 ║
║ from_list  ║  ╚══════╦══════════╝  ╚═══════════════════════╝
╚════════════╝         │ calls
              ╔════════▼═════════════════════════════════════╗
              ║  table/algorithms/  (all internal)           ║
              ║                                              ║
              ║  __init__.py  ← re-export facade             ║
              ║  _utils.py    ← array helpers                ║
              ║  _mips.py     ← MIPS core (NO CHANGES)       ║
              ║  _structure.py ← header/spanning/prefix      ║
              ║  _categorize.py ← split, row headers         ║
              ╚══════════════════════════════════════════════╝
              ╔═══════════════════════════════════════════════╗
              ║  table/footnotes.py  table/history.py         ║
              ║  table/parse.py      exceptions.py            ║
              ╚═══════════════════════════════════════════════╝
```

### 3.3 Data Flow

1. **Input:** `Table(source)` dispatches to `input/from_any.py`, which
   detects the source type (list → `from_list`, CSV → `from_csv`,
   HTML file or URL → `from_html`). URL detection uses `urllib.parse`
   (stdlib). HTML URLs are fetched with `requests`; if that fails and
   `selenium` is installed, the optional fallback is used. All paths
   return a `numpy.ndarray` of dtype `<U60`.

2. **Pre-processing:** `_analyze_table()` runs on init. The raw array is
   cleaned (`pre_clean`), spanning cells are duplicated, duplicate labels
   are prefixed, and footnotes are located and optionally inlined.

3. **MIPS algorithm:** `find_cc4` locates the data boundary; `find_cc1_cc2`
   finds the stub-header corner cells; `find_cc3` completes the four
   critical-cell set. Header extension (up and down) optionally expands
   the header region beyond the MIPS result.

4. **Output:** Properties (`data`, `row_header`, `col_header`, `labels`,
   `category_table`) compute views over the processed array on demand.
   `to_pandas()` builds a MultiIndex DataFrame via `output/to_pandas.py`.
   `to_csv()` writes the raw table. `__str__` returns a PrettyTable string.

---

## 4. Public Interface Contract

The stable surface that downstream projects depend on. All signatures are
identical to `tabledataextractor` 1.5.11.

### 4.1 Top-level exports

```python
from chemtabextract import (
    Table,
    TrivialTable,
    TDEError,
    InputError,
    MIPSError,
)
```

### 4.2 `Table`

```python
class Table:
    def __init__(
        self,
        file_path: str | list,
        table_number: int = 1,
        **kwargs,
    ) -> None: ...

    # Configuration keywords (all optional):
    #   use_title_row: bool = True
    #   use_prefixing: bool = True
    #   use_footnotes: bool = True
    #   use_spanning_cells: bool = True
    #   use_header_extension: bool = True
    #   use_max_data_area: bool = False
    #   standardize_empty_data: bool = True
    #   row_header: int | None = None
    #   col_header: int | None = None

    @property
    def raw_table(self) -> np.ndarray: ...
    @property
    def pre_cleaned_table(self) -> np.ndarray: ...
    @property
    def pre_cleaned_table_empty(self) -> np.ndarray: ...
    @property
    def labels(self) -> np.ndarray: ...
    @property
    def data(self) -> np.ndarray: ...
    @property
    def row_header(self) -> np.ndarray: ...
    @property
    def col_header(self) -> np.ndarray: ...
    @property
    def stub_header(self) -> np.ndarray: ...
    @property
    def category_table(self) -> list: ...
    @property
    def footnotes(self) -> list: ...
    @property
    def title_row(self) -> list | None: ...
    @property
    def subtables(self) -> list[Table]: ...
    @property
    def row_categories(self) -> TrivialTable | None: ...
    @property
    def history(self) -> History: ...
    @property
    def configs(self) -> dict: ...

    def contains(self, pattern: str) -> bool: ...
    def transpose(self) -> None: ...
    def to_pandas(self) -> pd.DataFrame: ...
    def to_csv(self, file_path: str) -> None: ...
    def print(self) -> None: ...
    def print_raw_table(self) -> None: ...
```

### 4.3 `TrivialTable`

Subclass of `Table`. Configuration keywords differ:

```python
class TrivialTable(Table):
    def __init__(
        self,
        file_path: str | list,
        table_number: int = 1,
        **kwargs,
    ) -> None: ...

    # Configuration keywords:
    #   standardize_empty_data: bool = False
    #   clean_row_header: bool = False
    #   row_header: int = 0
    #   col_header: int = 0
```

### 4.4 Exceptions

```python
class TDEError(Exception): ...          # base class
class InputError(TDEError): ...         # bad input (empty, wrong type, bad path)
class MIPSError(TDEError): ...          # MIPS algorithm failure (malformed table)
```

`MIPSError` is raised from `category_table`, `data`, `row_header`,
`col_header`, `stub_header` if critical cells were not found.
`InputError` is raised from `__init__` for empty tables, 1D arrays, or
unrecognised input types.

### 4.5 Stability & thread-safety

- All properties are synchronous and blocking.
- `Table` objects are **not thread-safe** — do not share a single instance
  across threads. Construct a new `Table` per thread.
- No async support. Not planned for this iteration.
- The public API is considered **pre-stable** at `0.x.y`. MINOR version
  bumps may introduce breaking changes; these will be documented in
  `CHANGELOG.md` with a migration note.

---

## 5. Technology Stack

| Layer | Technology | Version constraint | Status | Rationale |
|---|---|---|---|---|
| Language | Python | `>=3.13` | Retained | Team standard |
| Build / env | `uv` + `pyproject.toml` | latest | Retained | Team standard; `setup.py` removed |
| Array processing | `numpy` | `>=1.16,<2.0.0` | Retained | Core data structure; constraint inherited |
| HTML parsing | `beautifulsoup4` | `>=4.12.0` | Retained | HTML input path |
| HTTP fetching | `requests` | `>=2.21.0` | Retained | Primary URL fetch |
| URL validation | `urllib.parse` (stdlib) | — | New (replaces Django) | Zero-dependency replacement |
| Symbolic math | `sympy` | `>=1.14.0` | Retained | MIPS factorization |
| Console output | `prettytable` | `>=0.7.2` | Retained | `__str__` on Table |
| DataFrame output | `pandas` | `>=0.23.4` | Retained | `to_pandas()` |
| JS-rendered URLs | `selenium` | `>=3.141.0` | Retained as **optional** `[web]` | Fallback only |
| Linting/formatting | `ruff` | latest | New | Team standard |
| Type checking | `mypy` | latest | New | Permissive initially |
| Security scan | `bandit` | latest | New | CDE2 policy |
| Dead code | `vulture` | latest | New | CDE2 policy |
| Complexity gate | `xenon` | latest | New | CDE2 policy |
| Testing | `pytest` + `pytest-cov` | latest | New (replaces unittest runner) | Team standard |
| Version management | `commitizen` | latest | New | Team standard |
| Django | — | — | **Removed** | Was used only for URLValidator |
| `setup.py` | — | — | **Removed** | Replaced by pyproject.toml |

---

## 6. Data Model

No persistent storage. All processing is in-memory on `numpy.ndarray` of
dtype `<U60` (fixed-width Unicode strings, max 60 characters per cell).

The `category_table` output is a Python `list` of `[data, row_cats, col_cats]`
triples, where `row_cats` and `col_cats` are themselves lists of strings.

No migration tooling required. No schema changes in this iteration.

---

## 7. Dependency Inventory

### Runtime (inherited by consuming projects)

| Package | Version constraint | Rationale |
|---|---|---|
| `numpy` | `>=1.16,<2.0.0` | Core array type throughout |
| `sympy` | `>=1.14.0` | MIPS algorithm factorization |
| `beautifulsoup4` | `>=4.12.0` | HTML table parsing |
| `requests` | `>=2.21.0` | URL fetching |
| `prettytable` | `>=0.7.2` | Console output |
| `pandas` | `>=0.23.4` | DataFrame output |

### Optional extras

| Extra | Package | Notes |
|---|---|---|
| `[web]` | `selenium>=3.141.0` | JS-rendered URL fallback only |

### Development / tooling (not inherited)

| Package | Group | Notes |
|---|---|---|
| `pytest` | `dev` | Test runner |
| `pytest-cov` | `dev` | Coverage measurement |
| `pre-commit` | `dev` | Hook runner |
| `ruff` | `dev` | Lint + format |
| `mypy` | `dev` | Type checking |
| `bandit` | `dev` | Security scan |
| `vulture` | `dev` | Dead code detection |
| `xenon` | `dev` | Complexity gate |
| `commitizen` | `dev` | Conventional commits + changelog |

### Documentation (not inherited)

| Package | Group | Notes |
|---|---|---|
| `sphinx` | `docs` | |
| `m2r` | `docs` | Markdown → RST |
| `nbsphinx` | `docs` | Notebook integration |
| `nbsphinx-link` | `docs` | |
| `jinja2` | `docs` | Sphinx templating |
| `ipykernel` | `docs` | Notebook execution |

---

## 8. Testing Strategy

### Unit tests

All existing test files migrated to native `pytest` style (functions and
fixtures; no `unittest.TestCase`). Test data files in `tests/data/` are
unchanged. Shared fixtures (e.g. commonly used `Table` instances) live in
`tests/conftest.py`.

### New tests

| File | Purpose |
|---|---|
| `tests/test_url_validation.py` | Parametrised tests for `from_any.url()`: valid `http://`, `https://`, `ftp://` URLs accepted; bare hostnames, private IPs, empty strings, non-URL paths rejected. Covers SSRF-adjacent edge cases. |
| `tests/test_public_interface.py` | Import smoke test: asserts all public symbols are importable from `chemtabextract` top level. Acts as a lightweight downstream-consumer integration test. |

### Coverage

- Measured with `pytest-cov`, scoped to `src/chemtabextract/`
- Gate: `--cov-fail-under=40` (current baseline; ratchet upward in future PRs)
- Baseline recorded on first passing run and committed to `pyproject.toml`
  as the floor

### Pre-commit hook execution

`pytest --cov=chemtabextract --cov-report=term-missing --cov-fail-under=40`
runs as the final pre-commit hook. Can be skipped locally with
`SKIP=pytest-cov git commit` if justified.

### Mocking approach

- Network calls in `from_html.py` (`requests.get`, `selenium`) are mocked
  in any test that exercises the URL path
- No live network calls in the test suite

---

## 9. Versioning and Release Policy

- **Scheme:** Semantic versioning (`MAJOR.MINOR.PATCH`)
- **Starting version:** `0.8.0` — signals functional parity with upstream
  `tabledataextractor` 1.5.11 in a pre-stable release
- **Pre-1.0 convention:** MINOR bump for any change to the public API
  (additions or removals); PATCH for bug fixes and internal refactors
- **Breaking change definition:** Any removal of or incompatible change to
  `Table`, `TrivialTable`, or their public properties/methods; any removal
  of `TDEError`, `InputError`, or `MIPSError` from the top-level namespace
- **Deprecation policy:** Not applicable at `0.x.y`; to be defined when
  approaching `1.0.0`
- **CHANGELOG:** Maintained in `CHANGELOG.md`; generated and updated via
  `cz changelog`. Initialised with a `0.8.0` entry documenting the fork
  point from `tabledataextractor` 1.5.11
- **Version source of truth:** `version` field in `[project]` section of
  `pyproject.toml`; managed via `commitizen` with `version_provider = "pep621"`
- **PyPI publication:** Out of scope for this iteration

---

## 10. Observability

All modules use `logging.getLogger(__name__)`. No handlers, formatters, or
`basicConfig` calls anywhere in the library code.

`chemtabextract/__init__.py` installs a `NullHandler` on the package logger
(Python library best practice):

```python
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

Callers (e.g. CDE2) configure logging as they see fit. The existing log
messages (`INFO` for init/config, `DEBUG` for algorithm steps, `CRITICAL` for
unrecoverable errors) are preserved unchanged.

---

## 11. Requirement Gaps and Architectural Defaults Applied

| Gap | Decision | Approved by |
|---|---|---|
| Starting version number | `0.8.0` (pre-stable parity signal) | Product owner (session 2026-03-16) |
| CHANGELOG initialisation | `cz changelog` at `0.8.0` fork point | Architectural default; accepted |
| URL validation replacement scope | `urllib.parse` + scheme whitelist (`http`, `https`, `ftp`) + new parametrised regression tests | Architectural default; accepted |
| Runtime vs dev/docs deps | Sphinx family → `[dependency-groups] docs`; test/lint tools → `[dependency-groups] dev` | Confirmed by product owner |
| Test style migration | Migrate all tests to native `pytest` in this iteration | Confirmed by product owner |
| Exception import location | Re-exported from `chemtabextract.__init__` (Option A) | Confirmed by product owner |
| `openspec/` directory | Add to `.gitignore` (OpenSpec tooling artefact) | Confirmed by product owner |

---

## 12. Open Questions and Deferred Decisions

| Question | Owner | Target |
|---|---|---|
| PyPI publication plan (private index, GitHub Packages, or public PyPI)? | Cambridge Mol. Eng. team lead | Before 1.0.0 |
| Will `chemtabextract` ever need to selectively back-port upstream bug fixes? | Team lead | Ongoing |
| Lift `numpy < 2.0.0` constraint? | Whoever monitors numpy releases | Future iteration |
| Replace `selenium` with `playwright` as the optional web extra? | Any contributor | Future iteration |
| Tighten mypy from permissive to strict (module by module)? | Any contributor | Future iterations (P4) |
| Add `py.typed` marker? | Any contributor | After meaningful type coverage exists |
| GitHub Actions CI workflow? | Any contributor | Next iteration after this one |
| Push coverage above 40%? | Any contributor | Subsequent PRs (ratchet strategy) |
