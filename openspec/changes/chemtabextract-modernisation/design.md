## Context

`tabledataextractor` 1.5.11 is the upstream origin. This fork freezes algorithmic and API behaviour and performs structural modernisation only. The primary downstream consumer is **ChemDataExtractor 2 (CDE2)**, which imports `Table` and `TrivialTable` directly. The repackaged library must be installable via `uv` as a `pyproject.toml` dependency.

Current pain points:
- `setup.py` prevents clean `pyproject.toml`-only builds
- Django is a heavyweight runtime dep used only for `URLValidator`
- `selenium` is unconditionally imported, breaking environments where it is absent
- `logging.basicConfig` + `FileHandler` in `__init__.py` writes `tde_log.txt` and hijacks the root logger in any consuming application
- `algorithms.py` is a ~1000-line monolith mixing utilities, MIPS core, structure logic, and categorisation logic
- Tests are `unittest.TestCase` style, incompatible with the team's `pytest`-native tooling

## Goals / Non-Goals

**Goals:**
- Importable as `from chemtabextract import Table, TrivialTable` with identical behaviour to `tabledataextractor` 1.5.11
- Clean `pyproject.toml` + `uv` build with no `setup.py`
- Zero Django runtime dependency
- Selenium available only as `[web]` optional extra with graceful `ImportError`
- Library-safe logging (NullHandler only; no file creation, no root logger pollution)
- `algorithms.py` split into four focused sub-modules with a re-export facade so `table.py` is unchanged
- Full test suite passing under `pytest`; coverage baseline ≥40%
- Pre-commit quality gate passing clean

**Non-Goals:**
- Any change to MIPS algorithm logic
- Any change to public API signatures or behaviour
- Async support
- PyPI publication
- Full mypy strict mode
- GitHub Actions CI workflow
- Replacing selenium with playwright
- Pushing coverage above 40% in this iteration

## Decisions

### D1 — src/ layout
**Decision:** Adopt `src/chemtabextract/` layout.
**Rationale:** Prevents accidental imports of the source tree instead of the installed package during test runs. Standard Python best practice. `pyproject.toml` build backend (`hatchling` or `flit_core`) trivially supports it via `packages` configuration.
**Alternatives considered:** Keep flat layout — rejected because it perpetuates an anti-pattern and makes future packaging harder.

### D2 — URL validation: urllib.parse over any third-party library
**Decision:** Replace Django's `URLValidator` with a two-line `urllib.parse` check: `scheme in {"http", "https", "ftp"} and bool(result.netloc)`.
**Rationale:** Zero new dependencies. The check is functionally equivalent for the use case (detecting whether a string is a fetchable URL vs a local path/CSV). Private IPs are accepted — SSRF is the caller's responsibility, not the library's.
**Alternatives considered:** `validators` library — unnecessary dep. `furl` — unnecessary dep. Keep Django — the entire motivation is to remove it.

### D3 — Selenium guard strategy
**Decision:** Top-level `try/except ImportError` in `from_html.py` sets `_SELENIUM_AVAILABLE: bool`. If `False` and `requests` also fails, raise `InputError` with an install hint.
**Rationale:** Avoids conditional imports deep in call paths. Fails fast with a clear message rather than a confusing `NameError`.

### D4 — algorithms.py split: move, not rewrite
**Decision:** Move functions verbatim into four new sub-modules. The `algorithms/__init__.py` re-exports every symbol imported by `table.py`, so `table.py` needs no changes.
**Rationale:** Zero risk of introducing regressions — diff is purely mechanical file moves. The re-export facade keeps the internal import surface stable.
**Constraint:** `_mips.py` is carved out last and must be an exact copy — no formatting changes, no renames, no refactors. It is excluded from ruff formatting and mypy checking via per-module overrides.

### D5 — Milestone sequencing
**Decision:** Six sequential milestones, each on its own feature branch, merged to `main` only after full test suite passes.
```
M0 (rename/src) → M1 (deps) + M2 (logging) → M3 (split) → M4 (pytest) → M5 (pre-commit)
```
M1 and M2 may be parallelised or combined. M3 depends on M2 (dead code removed). M5 is always last.
**Rationale:** Each milestone leaves the repo in a deployable state. Avoids one giant PR that is impossible to review.

### D6 — NullHandler placement
**Decision:** Install NullHandler in `chemtabextract/__init__.py` only.
**Rationale:** Python library best practice (PEP 8, logging HOWTO). All other modules use `logging.getLogger(__name__)` and emit messages normally — it is the consuming application's responsibility to configure handlers.

### D7 — Coverage gate
**Decision:** Set `--cov-fail-under=40` as the initial baseline. Record the exact measured percentage in `pyproject.toml` and ratchet upward in future PRs.
**Rationale:** The existing test suite was written against a flat layout and exercises the core algorithm paths well; 40% is achievable immediately. Forcing 80%+ before any new tests are written would block the pre-commit gate.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| MIPS regression during algorithms split | Full test suite is the regression guard. Zero logic changes permitted. Use `git diff` to confirm functions are verbatim copies. |
| urllib.parse accepts/rejects different URL forms than Django's URLValidator | Parametrised regression tests in `test_url_validation.py` cover all known cases. The URL function is used only to distinguish "is this a URL?" from "is this a local path?" |
| xenon blocks pre-commit due to MIPS complexity | Calibrate `--max-absolute` against current codebase before enforcing. `find_cc1_cc2` complexity is known and intentional; document the threshold choice. |
| pytest migration introduces subtle fixture scoping differences | Migrate one file at a time; run full suite after each file before proceeding. |
| selenium optional guard causes unexpected ImportError in existing code paths | Guard is tested explicitly. `InputError` with install hint is surfaced to caller. |
| CDE2 integration fails on drop-in rename | Test CDE2 against local path reference (`chemtabextract = { path = "../tabledataextractor", editable = true }`) before updating dep declaration. |

## Migration Plan

1. **M0** — Rename and migrate. Delete local `.venv`, recreate with `uv sync`. Update any local scripts using `from tabledataextractor import ...`.
2. **M1** — Dependency cleanup. `uv sync` picks up Django removal and selenium demotion automatically.
3. **M2** — Logging fix. `tde_log.txt` will no longer be created. Remove any `.gitignore` entry for it.
4. **M3** — Algorithm split. No consumer-visible changes; internal only.
5. **M4** — pytest migration. Run `uv run pytest tests/` to verify.
6. **M5** — Pre-commit. Run `pre-commit install` then `pre-commit run --all-files`. Fix all findings before committing.

**CDE2 update (after M0):**
```toml
# Replace in CDE2's pyproject.toml:
chemtabextract = { path = "../tabledataextractor", editable = true }
# Later, once published:
chemtabextract >= 0.8.0
```

**Rollback:** Each milestone is a separate branch. Roll back by reverting the merge commit for that milestone. Milestones are independent enough that partial rollback is safe (except M3 depends on M2, M5 depends on all).

## Open Questions

| Question | Owner | Target |
|---|---|---|
| PyPI publication plan (private index, GitHub Packages, public PyPI)? | CME team lead | Before 1.0.0 |
| Lift `numpy < 2.0.0` constraint? | Whoever monitors numpy releases | Future iteration |
| Replace selenium with playwright as optional web extra? | Any contributor | Future iteration |
| Tighten mypy from permissive to strict? | Any contributor | Future iterations |
| GitHub Actions CI workflow? | Any contributor | Next iteration |
