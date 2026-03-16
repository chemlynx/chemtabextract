## 1. Milestone 0 — Rename & src/ Migration (branch: feat/milestone-0-rename-src-layout)

- [ ] 1.1 Create `src/chemtabextract/` directory tree mirroring the current `tabledataextractor/` structure exactly (preserve sub-directory layout)
- [ ] 1.2 Move all source files into `src/chemtabextract/`; update every `from tabledataextractor.X import Y` → `from chemtabextract.X import Y` across all source files
- [ ] 1.3 Update `pyproject.toml`: set `name = "chemtabextract"`, `version = "0.8.0"`, configure build backend for `src/` layout, add `[tool.commitizen]` section with `version_provider = "pep621"`
- [ ] 1.4 Remove `setup.py` from the repository
- [ ] 1.5 Update all `from tabledataextractor` imports in `tests/` to `from chemtabextract` (mechanical find-and-replace; no logic changes)
- [ ] 1.6 Verify `uv run pytest tests/` passes in full; confirm `from tabledataextractor import Table` raises `ModuleNotFoundError`
- [ ] 1.7 Commit: `feat: rename package to chemtabextract and migrate to src/ layout`
- [ ] 1.8 Merge `feat/milestone-0-rename-src-layout` → `main`

## 2. Milestone 1 — Dependency Cleanup (branch: feat/milestone-1-dependency-cleanup)

- [ ] 2.1 Replace `from django.core.validators import URLValidator` in `src/chemtabextract/input/from_any.py` with a `urllib.parse` implementation returning `True` for `http`/`https`/`ftp` URLs with non-empty netloc
- [ ] 2.2 Remove `django` from `[project.dependencies]` in `pyproject.toml`
- [ ] 2.3 Remove `selenium` from `[project.dependencies]`; add `[project.optional-dependencies] web = ["selenium>=3.141.0"]`
- [ ] 2.4 Add `_SELENIUM_AVAILABLE` flag via top-level `try/except ImportError` in `from_html.py`; raise `InputError` with install hint if selenium is absent and requests fails
- [ ] 2.5 Move doc deps (sphinx, m2r, nbsphinx, nbsphinx-link, jinja2, ipykernel) to `[dependency-groups] docs` in `pyproject.toml`
- [ ] 2.6 Add `[dependency-groups] dev` with: pytest, pytest-cov, pre-commit, ruff, mypy, bandit, vulture, xenon, commitizen
- [ ] 2.7 Write `tests/test_url_validation.py` with parametrised tests covering all URL cases in the dependency-management spec
- [ ] 2.8 Run `uv sync` and verify environment resolves without Django; verify full test suite passes
- [ ] 2.9 Commit: `feat: remove django, make selenium optional, fix dep groups`
- [ ] 2.10 Merge `feat/milestone-1-dependency-cleanup` → `main`

## 3. Milestone 2 — Logging Fix & Dead Code Removal (branch: feat/milestone-2-logging-dead-code)

- [ ] 3.1 Replace `logging.basicConfig(...)` and `FileHandler` block in `chemtabextract/__init__.py` with `logging.getLogger(__name__).addHandler(logging.NullHandler())`
- [ ] 3.2 Remove `__title__`, `__author__`, `__email__`, `__license__`, `__copyright__` module-level constants from `__init__.py`
- [ ] 3.3 Add re-exports to `__init__.py`: `from chemtabextract.exceptions import TDEError, InputError, MIPSError` and `from chemtabextract.table.table import Table, TrivialTable`
- [ ] 3.4 Delete `build_category_table` function from `src/chemtabextract/table/algorithms.py` (grep first to confirm no import sites reference it)
- [ ] 3.5 Write `tests/test_public_interface.py` with `test_top_level_imports()` and `test_no_log_file_created(tmp_path, monkeypatch)`
- [ ] 3.6 Verify full test suite passes; confirm `tde_log.txt` is not created
- [ ] 3.7 Commit: `fix: remove logging anti-pattern and dead build_category_table`
- [ ] 3.8 Merge `feat/milestone-2-logging-dead-code` → `main`

## 4. Milestone 3 — algorithms.py Split (branch: feat/milestone-3-algorithms-split)

- [ ] 4.1 Create `src/chemtabextract/table/algorithms/` directory and empty `__init__.py`
- [ ] 4.2 Create `_utils.py` — move verbatim: `empty_string`, `empty_cells`, `standardize_empty`, `pre_clean`, `clean_unicode`, `duplicate_rows`, `duplicate_columns`
- [ ] 4.3 Create `_mips.py` — move verbatim (zero logic/formatting changes): `find_cc4`, `find_cc1_cc2`, `find_cc3`
- [ ] 4.4 Create `_structure.py` — move verbatim: `find_title_row`, `find_note_cells`, `prefix_duplicate_labels`, `duplicate_spanning_cells`, `header_extension_up`, `header_extension_down`
- [ ] 4.5 Create `_categorize.py` — move verbatim: `categorize_header`, `split_table`, `find_row_header_table`, `clean_row_header`
- [ ] 4.6 Populate `algorithms/__init__.py` with re-exports of all symbols consumed by `table.py` (see design.md D4 for the exact import block)
- [ ] 4.7 Delete the original `src/chemtabextract/table/algorithms.py` file
- [ ] 4.8 Verify `table.py` is unchanged; verify `uv run pytest tests/` passes in full
- [ ] 4.9 Commit: `refactor: split algorithms.py into focused sub-modules`
- [ ] 4.10 Merge `feat/milestone-3-algorithms-split` → `main`

## 5. Milestone 4 — pytest Migration (branch: feat/milestone-4-pytest-migration)

- [x] 5.1 Create `tests/conftest.py` with at minimum a `table_example1` fixture; add further fixtures as migration reveals repeated patterns
- [x] 5.2 Migrate `test_input_from_csv.py` to native pytest; run suite; confirm green
- [x] 5.3 Migrate `test_output_from_csv.py` to native pytest; run suite; confirm green
- [x] 5.4 Migrate `test_trivial_table.py` to native pytest; run suite; confirm green
- [x] 5.5 Migrate `test_table_footnotes.py` to native pytest; run suite; confirm green
- [x] 5.6 Migrate `test_row_categories.py` to native pytest; run suite; confirm green
- [x] 5.7 Migrate `test_table_table_spanning_cells.py` to native pytest; run suite; confirm green
- [x] 5.8 Migrate `test_table_table_header_extension.py` to native pytest; run suite; confirm green
- [x] 5.9 Migrate `test_table_table_header_extens_d.py` to native pytest; run suite; confirm green
- [x] 5.10 Migrate `test_table_table_subtables.py` to native pytest; run suite; confirm green
- [x] 5.11 Migrate `test_table_table.py` to native pytest; run suite; confirm green
- [x] 5.12 Migrate `test_tde.py` to native pytest; run suite; confirm green
- [x] 5.13 Run `uv run pytest --cov=chemtabextract --cov-report=term-missing`; record measured coverage percentage; set `fail_under` in `pyproject.toml` `[tool.coverage.report]` to that value (must be ≥40)
- [x] 5.14 Add `[tool.pytest.ini_options]` and `[tool.coverage.run]` sections to `pyproject.toml`
- [x] 5.15 Verify zero `import unittest` references remain in `tests/`
- [ ] 5.16 Commit: `test: migrate test suite to native pytest; record coverage baseline`
- [ ] 5.17 Merge `feat/milestone-4-pytest-migration` → `main`

## 6. Milestone 5 — Pre-commit Stack (branch: feat/milestone-5-precommit-stack)

- [x] 6.1 Create `.pre-commit-config.yaml` with all required hook repos: pre-commit-hooks, ruff-pre-commit, mirrors-mypy, bandit, vulture, xenon, and local pytest-cov hook
- [x] 6.2 Add `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.mypy]`, `[[tool.mypy.overrides]]`, `[tool.bandit]`, and `[tool.commitizen]` sections to `pyproject.toml`
- [x] 6.3 Run `xenon --max-absolute C src/chemtabextract` to calibrate; set `--max-absolute` threshold in the xenon hook accordingly; add a comment documenting the MIPS complexity rationale
- [x] 6.4 Run `pre-commit run --all-files`; fix all ruff lint/format violations
- [x] 6.5 Run `pre-commit run --all-files`; investigate and resolve all bandit findings (suppress false positives with `# nosec` + inline comment)
- [x] 6.6 Run `pre-commit run --all-files`; create `whitelist.py` (or equivalent vulture config) for public API symbols that vulture flags as dead code
- [x] 6.7 Run `pre-commit run --all-files`; verify mypy passes under permissive config (fix any hard errors)
- [x] 6.8 Run `cz changelog --unreleased-version 0.8.0`; edit generated `CHANGELOG.md` entry to describe the fork from `tabledataextractor 1.5.11`
- [x] 6.9 Verify `pre-commit run --all-files` exits 0 on a clean working tree
- [ ] 6.10 Commit: `ci: install pre-commit stack; add CHANGELOG at 0.8.0`
- [ ] 6.11 Merge `feat/milestone-5-precommit-stack` → `main`
