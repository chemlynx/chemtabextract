# QA Developer Actions — post-verify-cleanups

> Raised by: QA Engineer review of commit b1b9ba3 (merge of fix/post-verify-cleanups)
> Date: 2026-03-17
> Scope: Four fixes addressing W1/W2/W3/S1 from the verify report —
>   `.pre-commit-config.yaml`, `from_any.py`,
>   `specs/logging-and-exceptions/spec.md`,
>   `specs/precommit-stack/spec.md`
>
> For each action below, the developer must either implement the fix or make
> a written case explaining why the fix is not required. All actions must be
> resolved before QA signs off and moves to Phase 4 (test implementation).

## How to use this file

1. Work through Actions in priority order (P0/P1 before P2/P3).
2. For each Action, either apply the fix or write a justification under
   **Resolution** explaining why the fix is not required.
3. P0/P1 Actions block Phase 4. P2/P3 Actions may be resolved concurrently
   with Phase 4.
4. Update the sign-off checklist at the bottom when each Action is resolved.

---

## Action 1 — P1 · pytest-cov pre-push hook fails to import chemtabextract

**Priority:** P1
**File:** `.pre-commit-config.yaml`, local `pytest-cov` hook (lines 57–63)

### What is wrong

The `pytest-cov` hook uses `entry: uv run pytest` with `language: system`.
When pre-commit spawns this hook, Python's site-packages `.pth` files are not
processed, so the editable-install pointer (`_chemtabextract.pth →
/home/dave/code/chemtabextract/src`) is never added to `sys.path`. The result
is a hard failure every time anyone runs `git push`:

```
pytest with coverage.....................................................Failed
- hook id: pytest-cov
- exit code: 4

ImportError while loading conftest 'tests/conftest.py'.
tests/conftest.py:5: in <module>
    from chemtabextract import Table
E   ModuleNotFoundError: No module named 'chemtabextract'
```

This means the entire pre-push coverage gate is silently dead — pushes go out
without coverage enforcement running. `uv run python -m pytest` works correctly
because `python -m` processes `.pth` files; `uv run pytest` (invoking the
console-script entry point) does not in this context.

### What a correct fix looks like

Change the hook `entry` from the console-script invocation to the module
invocation:

```yaml
# before
entry: uv run pytest

# after
entry: uv run python -m pytest
```

The `args` list is unchanged. No other hook configuration needs to change.

### What "no fix required" would need to argue

That `uv run pytest` is known to work correctly in the pre-commit environment
on this machine (e.g., because there is a `PYTHONPATH` or `UV_PROJECT_ROOT`
environment variable set globally that makes the editable install visible), AND
that this has been verified by running `pre-commit run pytest-cov
--hook-stage pre-push --all-files` and confirming exit code 0.

### Resolution

> **Fixed** in commit `c02c3ad`. Entry changed to `uv run python -m pytest`.
> Verified: `pre-commit run pytest-cov --hook-stage pre-push --all-files` exits 0.

---

## Action 2 — P3 · Spec requirement text references non-existent `algorithms.py` file path

**Priority:** P3
**File:** `openspec/changes/chemtabextract-modernisation/specs/logging-and-exceptions/spec.md`, line 34

### What is wrong

The requirement sentence reads:

> *"The dead `build_category_table` function that existed in
> `src/chemtabextract/table/algorithms.py` SHALL be removed."*

The module `algorithms.py` (a single file) no longer exists — it was already
refactored into the package `src/chemtabextract/table/algorithms/` (a
directory with `__init__.py`, `_categorize.py`, `_mips.py`, `_structure.py`,
`_utils.py`). The **scenario** at line 37 already uses the correct path
`algorithms/`; only the prose on line 34 is stale.

A future reader following the spec literally would look for a file that does
not exist, which erodes confidence in the spec as a reliable reference.

### What a correct fix looks like

Replace `algorithms.py` with `algorithms/` in the requirement sentence:

```markdown
# before
The dead `build_category_table` function that existed in
`src/chemtabextract/table/algorithms.py` SHALL be removed.

# after
The dead `build_category_table` function that existed in
`src/chemtabextract/table/algorithms/` SHALL be removed.
```

### What "no fix required" would need to argue

That the spec is intentionally describing the historical state (what it
was before refactoring) and that readers are expected to understand the
module was subsequently converted to a package. This would require a
parenthetical note to that effect in the spec text to be a coherent argument.

### Resolution

> **Fixed** in commit `c02c3ad`. Requirement prose now reads `algorithms/` to match
> the scenario path and the actual package structure on disk.

---

## Backlog Items (no action required before sign-off)

None discovered during this review beyond the two Actions above.

---

## Review notes (informational)

All four intended fixes were verified correct:

| Fix | File | Verdict |
|-----|------|---------|
| W1 — add 3 missing pre-commit hooks | `.pre-commit-config.yaml` | ✅ All three hooks present and passing |
| W2 — narrow `build_category_table` spec scope | `specs/logging-and-exceptions/spec.md` | ✅ Dead copy absent from `algorithms/`; live copy in `to_pandas.py` retained |
| W3 — remove spurious `_utils` mypy override from spec | `specs/precommit-stack/spec.md` | ✅ Spec and `pyproject.toml` consistent; only `_mips` has override |
| S1 — replace `os.path.isfile` with `Path.is_file()` | `src/chemtabextract/input/from_any.py` | ✅ Both `html()` and `csv()` updated; `os.path` import removed |

Test suite: **104/104 passing**, branch coverage **75.45%** (threshold: 40%).
`pre-commit run --all-files` exits 0 on the full 13-hook stack.

---

## Sign-off Checklist

| Action | Priority | Status | Resolved by |
|--------|----------|--------|-------------|
| Action 1 — pytest-cov entry point fix | P1 | ✅ Resolved | c02c3ad |
| Action 2 — `algorithms.py` path in spec text | P3 | ✅ Resolved | c02c3ad |

> **QA sign-off: GRANTED** — 2026-03-17
> All Actions resolved in commit `c02c3ad` (merged at `d082410`).
> Pre-push coverage gate verified passing. No open findings remain.
