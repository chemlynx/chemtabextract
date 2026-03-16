# Implementation Plan — chemtabextract

> **Spec reference:** TECHNICAL_SPEC.md
> **Date:** 2026-03-16
> **Version target:** 0.8.0

---

## Principles for This Build

- The public interface (`Table`, `TrivialTable`, exceptions) is frozen — no
  behaviour changes, only structural moves
- The MIPS algorithm logic (`_mips.py`) MUST NOT be semantically altered at
  any point; the full test suite is the regression guard
- Each milestone leaves the repository in a passing, committable state
- Tests are updated or written alongside structural changes — never after
- The existing test suite passes in full before and after every milestone

---

## Repository Preparation

Before any feature work, ensure the following are true:

- [ ] `pyproject.toml` has `requires-python = ">=3.13"` *(already done)*
- [ ] `openspec/` is added to `.gitignore`
- [ ] A working `uv` environment can be created: `uv sync`
- [ ] The existing test suite passes as-is against the current flat layout:
      `uv run pytest tests/`

These are preconditions, not a milestone. Fix anything blocking before
starting Milestone 0.

---

## Milestones

### Milestone 0 — Rename & `src/` Migration

**Goal:** The package is importable as `chemtabextract` from a `src/` layout.
All internal references updated. `setup.py` removed. No behaviour changes.

**Deliverables:**

- [ ] Create `src/chemtabextract/` directory tree mirroring current
      `tabledataextractor/` structure exactly
- [ ] Move all source files into `src/chemtabextract/`; update every
      `from tabledataextractor.X import Y` → `from chemtabextract.X import Y`
      across all source files
- [ ] Update `pyproject.toml`:
  - `name = "chemtabextract"`
  - `version = "0.8.0"`
  - `packages` / build backend configured for `src/` layout
  - `[tool.commitizen]` section added with `version_provider = "pep621"`
- [ ] Remove `setup.py`
- [ ] Update `tests/` — change all `from tabledataextractor` imports to
      `from chemtabextract` (mechanical find-and-replace; no logic changes)
- [ ] Update `tests/data/` paths if any are hardcoded to the old package name
- [ ] Verify: `uv run pytest tests/` passes in full

**Acceptance criteria:**
```python
from chemtabextract import Table, TrivialTable
t = Table('./tests/data/table_example1.csv')
assert t.category_table  # non-empty
```
Full test suite green. `from tabledataextractor` produces `ModuleNotFoundError`.

**Commit:** `feat: rename package to chemtabextract and migrate to src/ layout`

---

### Milestone 1 — Dependency Cleanup

**Goal:** Django removed. `selenium` demoted to optional. Dev/doc deps
correctly separated. No behaviour changes.

**Deliverables:**

- [ ] **Remove Django:** Replace `from django.core.validators import URLValidator`
      in `src/chemtabextract/input/from_any.py` with a stdlib implementation:

  ```python
  from urllib.parse import urlparse

  def url(name: str) -> bool:
      """Returns True if name is a valid HTTP/HTTPS/FTP URL."""
      try:
          result = urlparse(name)
          return result.scheme in {"http", "https", "ftp"} and bool(result.netloc)
      except ValueError:
          return False
  ```

- [ ] Remove `django` from `[project.dependencies]` in `pyproject.toml`
- [ ] Make `selenium` optional:
  - Remove from `[project.dependencies]`
  - Add `[project.optional-dependencies] web = ["selenium>=3.141.0"]`
  - Guard the selenium import in `from_html.py` with a try/except so a
    clean `ImportError` is raised if the fallback is attempted without it:

    ```python
    try:
        from selenium import webdriver
        # ... selenium option imports
        _SELENIUM_AVAILABLE = True
    except ImportError:
        _SELENIUM_AVAILABLE = False
    ```

  - In `read_url()`: if `_SELENIUM_AVAILABLE` is False and requests fails,
    raise `InputError("selenium is required for JS-rendered URLs. "
    "Install with: uv add chemtabextract[web]")`

- [ ] Move doc deps to `[dependency-groups] docs`:
      `sphinx`, `m2r`, `nbsphinx`, `nbsphinx-link`, `jinja2`, `ipykernel`
- [ ] Add `[dependency-groups] dev`:
      `pytest`, `pytest-cov`, `pre-commit`, `ruff`, `mypy`, `bandit`,
      `vulture`, `xenon`, `commitizen`
- [ ] Run `uv sync` and verify environment resolves without Django
- [ ] Write `tests/test_url_validation.py`:

  ```python
  import pytest
  from chemtabextract.input.from_any import url

  @pytest.mark.parametrize("value,expected", [
      ("http://example.com/table.html", True),
      ("https://example.com/table.html", True),
      ("ftp://example.com/table.csv", True),
      ("http://192.168.1.1/table.html", True),   # private IP — accepted (caller's responsibility)
      ("example.com/table.html", False),          # missing scheme
      ("not-a-url", False),
      ("", False),
      ("/local/path/table.csv", False),
      ("file:///etc/passwd", False),              # scheme not in whitelist
  ])
  def test_url_detection(value, expected):
      assert url(value) == expected
  ```

- [ ] Verify: `uv run pytest tests/` passes in full

**Acceptance criteria:** `uv add chemtabextract` (from local path) resolves
without Django. URL validation tests pass. Selenium import guarded cleanly.

**Commit:** `feat: remove django, make selenium optional, fix dep groups`

---

### Milestone 2 — Logging Fix & Dead Code Removal

**Goal:** Library no longer writes `tde_log.txt` or configures root logging.
Dead `build_category_table` removed from `algorithms.py`.

**Deliverables:**

- [ ] **Fix `__init__.py` logging:** Replace the `logging.basicConfig(...)`
      and `FileHandler` block with:

  ```python
  import logging
  logging.getLogger(__name__).addHandler(logging.NullHandler())
  ```

  Remove the `__title__`, `__author__`, `__email__`, `__license__`,
  `__copyright__` module-level constants (already in `pyproject.toml`).
  Retain `__version__` if referenced anywhere; otherwise remove.

- [ ] **Add exception re-exports to `__init__.py`:**

  ```python
  from chemtabextract.exceptions import TDEError, InputError, MIPSError
  from chemtabextract.table.table import Table, TrivialTable
  ```

- [ ] **Remove dead function:** Delete `build_category_table` (lines ~954–973)
      from `src/chemtabextract/table/algorithms.py`. Verify no import site
      references it (grep confirms it is not imported anywhere).

- [ ] Write `tests/test_public_interface.py`:

  ```python
  def test_top_level_imports():
      from chemtabextract import Table, TrivialTable
      from chemtabextract import TDEError, InputError, MIPSError
      assert Table is not None
      assert TrivialTable is not None
      assert issubclass(InputError, TDEError)
      assert issubclass(MIPSError, TDEError)

  def test_no_log_file_created(tmp_path, monkeypatch):
      """Importing chemtabextract must not create tde_log.txt."""
      monkeypatch.chdir(tmp_path)
      import importlib, chemtabextract
      importlib.reload(chemtabextract)
      assert not (tmp_path / "tde_log.txt").exists()
  ```

- [ ] Verify: `uv run pytest tests/` passes in full

**Acceptance criteria:** `tde_log.txt` is never created. All five symbols
importable from top level. `from chemtabextract import MIPSError` works.

**Commit:** `fix: remove logging anti-pattern and dead build_category_table`

---

### Milestone 3 — `algorithms.py` Split

**Goal:** `algorithms.py` monolith replaced by an `algorithms/` sub-package
with four focused internal modules. `table.py` import line unchanged.

**Deliverables:**

- [ ] Create `src/chemtabextract/table/algorithms/` directory
- [ ] Create `_utils.py` — move:
      `empty_string`, `empty_cells`, `standardize_empty`, `pre_clean`,
      `clean_unicode`, `duplicate_rows`, `duplicate_columns`
- [ ] Create `_mips.py` — move (logic verbatim, zero changes):
      `find_cc4`, `find_cc1_cc2`, `find_cc3`
- [ ] Create `_structure.py` — move:
      `find_title_row`, `find_note_cells`, `prefix_duplicate_labels`,
      `duplicate_spanning_cells`, `header_extension_up`, `header_extension_down`
- [ ] Create `_categorize.py` — move:
      `categorize_header`, `split_table`, `find_row_header_table`,
      `clean_row_header`
      *(dead `build_category_table` already removed in Milestone 2)*
- [ ] Create `algorithms/__init__.py` that re-exports every symbol currently
      imported by `table.py`:

  ```python
  # algorithms/__init__.py
  # Re-exports all symbols consumed by table.py.
  # Do not import sub-modules directly from outside this package.
  from chemtabextract.table.algorithms._utils import (
      empty_string, empty_cells, standardize_empty, pre_clean,
      clean_unicode, duplicate_rows, duplicate_columns,
  )
  from chemtabextract.table.algorithms._mips import (
      find_cc4, find_cc1_cc2, find_cc3,
  )
  from chemtabextract.table.algorithms._structure import (
      find_title_row, find_note_cells, prefix_duplicate_labels,
      duplicate_spanning_cells, header_extension_up, header_extension_down,
  )
  from chemtabextract.table.algorithms._categorize import (
      categorize_header, split_table, find_row_header_table, clean_row_header,
  )
  ```

- [ ] Delete the original `algorithms.py` file
- [ ] **Do not change `table.py`** — its import line
      `from chemtabextract.table.algorithms import ...` continues to work
      through the `__init__.py` facade
- [ ] Verify: `uv run pytest tests/` passes in full — this is the primary
      regression guard for this milestone

**Acceptance criteria:** Full test suite green. `table.py` unchanged.
`from chemtabextract.table.algorithms._mips import find_cc1_cc2` works
(internal access still possible; just not recommended for downstream).

**Commit:** `refactor: split algorithms.py into focused sub-modules`

---

### Milestone 4 — pytest Migration

**Goal:** All `unittest.TestCase` tests migrated to native `pytest` functions
and fixtures. Test coverage baseline measured.

**Deliverables:**

- [ ] Create `tests/conftest.py` with shared fixtures. At minimum:

  ```python
  import pytest
  from chemtabextract import Table

  @pytest.fixture
  def table_example1():
      return Table('./tests/data/table_example1.csv')
  ```

  Add further fixtures as the migration reveals repeated setup patterns.

- [ ] Migrate each test file in turn (safest order — least to most complex):
  1. `test_input_from_csv.py`
  2. `test_output_from_csv.py`
  3. `test_trivial_table.py`
  4. `test_table_footnotes.py`
  5. `test_row_categories.py`
  6. `test_table_table_spanning_cells.py`
  7. `test_table_table_header_extension.py`
  8. `test_table_table_header_extens_d.py`
  9. `test_table_table_subtables.py`
  10. `test_table_table.py`
  11. `test_tde.py`

  Migration rules per file:
  - `class TestFoo(unittest.TestCase):` → remove class wrapper; functions
    become top-level `def test_*():`
  - `self.assertEqual(a, b)` → `assert a == b`
  - `self.assertListEqual(a, b)` → `assert a == b`
  - `self.assertTupleEqual(a, b)` → `assert a == b`
  - `self.assertTrue(x)` → `assert x`
  - `self.assertRaises(Exc)` → `pytest.raises(Exc)`
  - `setUp` / `tearDown` methods → `@pytest.fixture` with `yield` or
    `autouse=True` in `conftest.py`
  - Remove all `import unittest` statements
  - Remove `if __name__ == '__main__': unittest.main()`

- [ ] After each file migration: `uv run pytest tests/` must pass before
      proceeding to the next file

- [ ] Run `uv run pytest --cov=chemtabextract --cov-report=term-missing`
      and **record the coverage percentage** in `pyproject.toml`:

  ```toml
  [tool.pytest.ini_options]
  addopts = "--cov=chemtabextract --cov-report=term-missing"

  [tool.coverage.run]
  source = ["chemtabextract"]

  [tool.coverage.report]
  fail_under = 40   # update this number to the measured baseline
  ```

**Acceptance criteria:** Zero `unittest` imports remain in `tests/`. Full
test suite passes under `pytest`. Coverage baseline recorded and ≥ 40%.

**Commit:** `test: migrate test suite to native pytest; record coverage baseline`

---

### Milestone 5 — Pre-commit Stack

**Goal:** Full quality gate installed and passing on a clean checkout.

**Deliverables:**

- [ ] Create `.pre-commit-config.yaml`. Use frozen-hash (`# frozen: vX.Y.Z`)
      style for all hook revisions, matching CDE2 convention:

  ```yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: # frozen: vX.Y.Z
      hooks:
        - id: trailing-whitespace
        - id: end-of-file-fixer
        - id: check-yaml
        - id: check-added-large-files
        - id: check-merge-conflict
        - id: debug-statements

    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: # frozen: vX.Y.Z
      hooks:
        - id: ruff
          args: [--fix, --exit-non-zero-on-fix]
        - id: ruff-format

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: # frozen: vX.Y.Z
      hooks:
        - id: mypy
          args: [--config-file=pyproject.toml]

    - repo: https://github.com/PyCQA/bandit
      rev: # frozen: vX.Y.Z
      hooks:
        - id: bandit
          args: [-c, pyproject.toml]

    - repo: https://github.com/jendrikseipp/vulture
      rev: # frozen: vX.Y.Z
      hooks:
        - id: vulture
          args: [src/chemtabextract, --min-confidence=80]

    - repo: https://github.com/rubik/xenon
      rev: # frozen: vX.Y.Z
      hooks:
        - id: xenon
          args:
            - --max-absolute=B
            - --max-modules=B
            - --max-average=A
            - src/chemtabextract

    - repo: local
      hooks:
        - id: pytest-cov
          name: pytest with coverage
          entry: uv run pytest
          language: system
          pass_filenames: false
          always_run: true
  ```

  > **Note on xenon thresholds:** Run `xenon --max-absolute C src/chemtabextract`
  > against the current codebase first to calibrate. `find_cc1_cc2` will score
  > high — set `--max-absolute` to `B` or `C` to accommodate it, and document
  > the choice as intentional in a comment in the config or `pyproject.toml`.

- [ ] Add tool config sections to `pyproject.toml`:

  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py313"

  [tool.ruff.lint]
  select = ["E", "F", "W", "I"]

  [tool.mypy]
  python_version = "3.13"
  warn_return_any = false
  ignore_missing_imports = true

  [[tool.mypy.overrides]]
  module = ["chemtabextract.table.algorithms._mips",
            "chemtabextract.table.algorithms._utils"]
  ignore_errors = true

  [tool.bandit]
  exclude_dirs = ["tests"]
  skips = []

  [tool.commitizen]
  name = "cz_conventional_commits"
  version = "0.8.0"
  version_files = ["pyproject.toml:version"]
  version_provider = "pep621"
  tag_format = "v$version"
  ```

- [ ] Run `pre-commit run --all-files` and fix all findings:
  - ruff lint/format violations (expect some in the algorithmic code —
    fix formatting; suppress complexity warnings with `# noqa` only where
    unavoidable and commented)
  - bandit: investigate any findings; suppress false positives with
    `# nosec` + inline comment
  - vulture: add a `whitelist.py` for any symbols that are intentionally
    exported but appear unused to vulture (e.g. public API symbols only
    used by downstream consumers)
  - xenon: calibrate thresholds as noted above

- [ ] Initialise CHANGELOG:
  ```bash
  cz changelog --unreleased-version 0.8.0
  ```
  Edit the generated entry to describe the fork from `tabledataextractor`.

- [ ] Verify: `pre-commit run --all-files` exits 0

**Acceptance criteria:** `pre-commit run --all-files` clean. `CHANGELOG.md`
exists with a `0.8.0` entry. All hooks run without suppressed failures
(except documented intentional suppressions for MIPS complexity).

**Commit:** `ci: install pre-commit stack; add CHANGELOG at 0.8.0`

---

## Dependency Graph

```
[Repo prep]
    │
    ▼
Milestone 0 — Rename & src/ layout
    │
    ▼
Milestone 1 — Dependency cleanup       ← can start once M0 is green
    │
    ▼
Milestone 2 — Logging fix & dead code  ← can start once M0 is green
    │                                     (parallel with M1 if desired)
    ▼
Milestone 3 — algorithms split         ← requires M0, M2 (dead code gone)
    │
    ▼
Milestone 4 — pytest migration         ← requires M0; can run after M3
    │                                     or parallel with M3 if careful
    ▼
Milestone 5 — pre-commit stack         ← requires M1, M2, M3, M4 all green
```

Milestones 1 and 2 may be worked in parallel or combined into a single PR
if the implementer prefers. Milestone 3 must follow Milestone 2 (dead code
removal reduces scope of the split). Milestone 5 should be the last thing
installed — it is easier to fix all pre-commit findings in one pass once the
codebase is fully restructured.

---

## Migration Notes

### For developers on this repository

1. After Milestone 0: delete any local `.venv` and recreate with `uv sync`
   to pick up the new package name
2. Any local scripts or notebooks using `from tabledataextractor import ...`
   must be updated to `from chemtabextract import ...`
3. `tde_log.txt` will no longer be created after Milestone 2 — remove any
   `.gitignore` entry for it if one exists

### For CDE2 maintainers

Once Milestone 0 is complete and the package is installable:

```toml
# In CDE2's pyproject.toml, replace:
# tabledataextractor>=1.5.11
# with:
chemtabextract>=0.8.0
```

Run the CDE2 test suite against the local `chemtabextract` path reference
before updating the declaration:

```toml
chemtabextract = { path = "../tabledataextractor", editable = true }
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| MIPS algorithm regression during algorithms split (M3) | Low | High | Full test suite must pass before and after; zero logic changes permitted; use `git diff` to confirm only moves |
| urllib.parse rejects a URL form that Django accepted, breaking URL-based tests | Low | Medium | URL regression tests written in M1 cover the known cases; no live-URL tests exist to break |
| xenon blocks initial pre-commit commit due to MIPS complexity | Medium | Low | Calibrate thresholds against current codebase before enforcing; `find_cc1_cc2` complexity is known and intentional |
| pytest migration introduces subtle test behaviour changes (e.g. fixture scoping) | Low | Medium | Migrate one file at a time; run suite after each file |
| selenium optional guard causes unexpected `ImportError` in existing code paths | Low | Low | Guard tested explicitly in URL validation tests; `InputError` with clear message surfaced to caller |
| CDE2 integration fails on drop-in rename | Low | High | Test CDE2 against local path reference before updating dep declaration |

---

## Out of Scope

The following are explicitly **not** part of this implementation plan:

- Any changes to MIPS algorithm logic
- New table-extraction features
- Replacing `selenium` with `playwright`
- Async support
- PyPI publication
- Full type annotation of the codebase (mypy starts permissive)
- Adding `py.typed` marker
- GitHub Actions CI workflow
- Pushing test coverage above 40%
- Rebuilding the documentation site
- Upstream synchronisation with `tabledataextractor`
