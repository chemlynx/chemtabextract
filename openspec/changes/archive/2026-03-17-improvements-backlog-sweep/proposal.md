## Why

The QA review of the modernisation work identified a backlog of correctness,
code quality, architecture, type-safety, and documentation issues spread across
the codebase. These issues — tracked in `IMPROVEMENTS.md` — range from silent
data-loss bugs (dtype truncation, TypeError mis-construction) through dead code,
API fragility, and missing type annotations. Addressing the development-owned
items now raises overall code quality and reduces maintenance risk before the
next feature cycle.

## What Changes

- **E1** — Fix `TypeError` construction in `create_table()` so the message
  string is clean
- **E2** — Remove pointless `try/except/raise` passthrough in `_analyze_table()`
- **E3** — Fix double property access to `_default_configs` in `_set_configs()`
- **Q1** — Rename `list_as_PrettyTable` → `list_as_pretty_table` (PEP 8);
  update all call-sites
- **Q2** — Cache `prefixed_row_or_column()` result instead of calling twice
- **Q3** — Add setter / update API to `History` so callers stop reaching into
  private attributes
- **Q4** — Return a copy from `Table.configs` property to prevent accidental
  external mutation
- **Q5** — Guard `CellParser.cut()` against 1-D array input with a clear error
- **Q6** — Fix `makearray()` corner-cell fill for combined `colspan`+`rowspan`
- **Q7** — Replace hard-coded `dtype="<U60"` with dynamic width derived from
  cell lengths; warn on truncation
- **Q8** — Remove unused `categorize_header()` export and its sole dependency
  import (`sympy.factor_list`)
- **Q9** — Remove dead pandas `MultiIndex.labels` compatibility branch; raise
  pandas floor to `>=0.25`
- **A1** — Cache `_cc4` / `_cc3` results as instance attributes after the table
  is fully prepared (architectural pre-work: pass `pre_cleaned_table` explicitly)
- **A2** — Add inline ordering comments to `_analyze_table()` documenting
  required prior state for each step
- **T1** — Add type hints to all public API functions listed in IMPROVEMENTS.md
- **D1** — Fix all incorrect / incomplete docstrings listed in IMPROVEMENTS.md

## Capabilities

### New Capabilities

- `history-update-api`: `History` exposes setter methods so callers don't
  mutate private attributes directly

### Modified Capabilities

- `algorithms-subpackage`: `prefixed_row_or_column` call-pattern changed;
  `categorize_header` removed from public facade; `_cc4`/`_cc3` caching added
- `logging-and-exceptions`: `TypeError` construction fixed; truncation warning
  added for dtype overflow
- `package-structure`: pandas floor raised; `sympy` dependency potentially
  trimmed from core

## Impact

- `src/chemtabextract/input/from_any.py` — E1
- `src/chemtabextract/input/from_csv.py` — Q7, T1
- `src/chemtabextract/input/from_html.py` — Q6, Q7, T1
- `src/chemtabextract/input/from_list.py` — Q7, T1
- `src/chemtabextract/table/table.py` — E2, E3, Q3, Q4, A1, A2, T1
- `src/chemtabextract/table/history.py` — Q3, D1, T1
- `src/chemtabextract/table/parse.py` — Q5, T1
- `src/chemtabextract/table/algorithms/_structure.py` — Q2, Q3, A1
- `src/chemtabextract/table/algorithms/_categorize.py` — Q8
- `src/chemtabextract/table/algorithms/__init__.py` — Q8
- `src/chemtabextract/output/print.py` — Q1
- `src/chemtabextract/output/to_pandas.py` — Q9, D1, T1
- `pyproject.toml` — Q9 (pandas floor)
- No public API breaking changes except `list_as_PrettyTable` rename (internal use only)
