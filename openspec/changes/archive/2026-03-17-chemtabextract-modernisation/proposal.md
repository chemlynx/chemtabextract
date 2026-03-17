## Why

`tabledataextractor` 1.5.11 carries legacy baggage (Django, `setup.py`, root-level logging side-effects, a monolithic `algorithms.py`, and `unittest`-style tests) that blocks adoption as a clean library dependency for ChemDataExtractor 2. This iteration repackages it as `chemtabextract 0.8.0` — same algorithm, same public API, modern Python project hygiene.

## What Changes

- Package renamed from `tabledataextractor` → `chemtabextract`; version set to `0.8.0`
- Source tree migrated to `src/` layout (`src/chemtabextract/`)
- `setup.py` removed; `pyproject.toml` + `uv` is the sole build system
- Django dependency removed; URL validation replaced with `urllib.parse` (stdlib)
- `selenium` demoted from runtime to optional extra (`[web]`)
- Doc and dev tooling dependencies correctly separated into `[dependency-groups]`
- Logging anti-pattern removed; `NullHandler` installed on package logger
- Dead function `build_category_table` removed from `algorithms.py`
- `algorithms.py` monolith split into four focused internal sub-modules
- Test suite migrated from `unittest.TestCase` to native `pytest`
- Pre-commit quality gate installed (ruff, mypy, bandit, vulture, xenon, pytest-cov)
- `CHANGELOG.md` initialised at `0.8.0`

## Capabilities

### New Capabilities

- `package-structure`: `src/` layout, renamed package, updated `pyproject.toml`, `setup.py` removal
- `dependency-management`: Django removed, selenium optional, dev/doc dep groups correctly separated
- `logging-and-exceptions`: NullHandler logging, top-level exception re-exports, dead code removal
- `algorithms-subpackage`: `algorithms.py` monolith split into `_utils`, `_mips`, `_structure`, `_categorize` sub-modules with facade `__init__.py`
- `pytest-suite`: Full test suite migrated to native pytest; coverage baseline ≥40% recorded
- `precommit-stack`: `.pre-commit-config.yaml` with ruff, mypy, bandit, vulture, xenon, pytest-cov; `CHANGELOG.md` initialised

### Modified Capabilities

<!-- No existing specs — this is the first OpenSpec change on this repo -->

## Impact

- **Package name:** All downstream consumers (`from tabledataextractor import ...`) must update to `from chemtabextract import ...`
- **Dependencies removed:** `django` (runtime), `selenium` (now optional `[web]`)
- **No API behaviour changes:** `Table`, `TrivialTable`, `TDEError`, `InputError`, `MIPSError` signatures and semantics are identical to `tabledataextractor` 1.5.11
- **No algorithm changes:** MIPS core (`find_cc4`, `find_cc1_cc2`, `find_cc3`) logic is untouched
- **CDE2 integration:** Update `pyproject.toml` dep declaration from `tabledataextractor>=1.5.11` → `chemtabextract>=0.8.0`
