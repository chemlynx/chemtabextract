## 0.10.1 (2026-06-16)

Upgrade to **Python 3.14** and refresh all dependencies to current versions.

- `requires-python` raised to `>=3.14`; ruff target `py314`; mypy `python_version` 3.14
- numpy `<2.0` pin removed → `>=2.4` (numpy 1.x has no Python 3.14 wheels); pandas
  `>=3.0`, lxml `>=6.1`, beautifulsoup4 `>=4.15`, selenium `>=4.45`, and all dev/docs
  tooling bumped to current; `uv.lock` re-resolved
- pre-commit hook revisions bumped to match (pre-commit-hooks, ruff, mypy 2.x,
  bandit, vulture)
- commitizen configured to update the changelog on bump

### Fix

- replace deprecated `findAll` with `find_all` and route `colspan`/`rowspan`
  through a typed `_attr_int` helper (newer BeautifulSoup stubs type `Tag.get`
  as a union)
- add a 30s timeout to `requests.get` (bandit B113)
- drop a stale `categorize_header` vulture-whitelist entry

## 0.10.0 (2026-03-17)

- Full test-suite expansion (Phase 4): TC1–TC4 cases, shared conftest fixtures,
  output-module coverage
- `.serena/` added to `.gitignore`

## 0.9.0 (2026-03-17)

Improvements backlog sweep (E1–E3, Q1–Q9, A1–A2, T1, D1).

### Feat

- add type hints across the full public API (T1)
- improvements-backlog-sweep — E1–E3, Q1–Q9, A1–A2, T1, D1

### Fix

- correct `n_cols` colspan accounting and `skip_index` for combined spans
- dynamic numpy dtype in all input parsers; warn on cells >200 chars (Q7)
- correct TypeError construction, remove passthrough try/except, fix double
  property access (E1–E3)
- correctness fixes, lxml dependency, coverage gate at 75%

### Perf

- cache `_cc4`/`_cc3` after `_analyze_table` (A1/A2)

### Refactor

- add `_override_config` context manager; `configs` returns a copy (Q4)
- add `History` setter methods; migrate callers off private attributes (Q3)
- rename `list_as_PrettyTable`, cache prefix result, guard `CellParser.cut`,
  fix corner cells (Q1/Q2/Q5/Q6)

## 0.8.0 (2026-03-16)

This release is the first version of **chemtabextract**, a maintained fork of
[tabledataextractor](https://github.com/CambridgeMolecularEngineering/tabledataextractor)
1.5.11. No algorithm or API behaviour changes are made — this release is a
structural modernisation of the package.

Key changes from `tabledataextractor` 1.5.11:

- Package renamed from `tabledataextractor` → `chemtabextract`; migrated to `src/` layout
- Django dependency removed; URL validation reimplemented with `urllib.parse`
- Selenium demoted to an optional `[web]` extra
- Library logging pattern (`NullHandler`) applied; `tde_log.txt` no longer created
- `algorithms.py` split into focused sub-modules (`_mips`, `_structure`, `_categorize`, `_utils`)
- Test suite migrated from `unittest.TestCase` to native `pytest`
- Pre-commit stack installed (ruff, mypy, bandit, vulture, xenon, pytest-cov)

### Feat

- remove django, make selenium optional, fix dep groups
- rename package to chemtabextract and migrate to src/ layout

### Fix

- remove logging anti-pattern and dead build_category_table

### Refactor

- split algorithms.py into focused sub-modules
