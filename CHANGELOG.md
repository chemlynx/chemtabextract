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
