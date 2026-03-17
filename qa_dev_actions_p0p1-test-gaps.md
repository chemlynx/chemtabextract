# QA Developer Actions — P0/P1 test-gap fixes

> Raised by: QA Engineer review of commit f2edc1f
> Date: 2026-03-17
> Scope: All 16 files changed in commit f2edc1f ("test: address P0/P1 test gaps
>   from QA review") — 7 production files and 5 test files.
>
> For each action below, the developer must either implement the fix or make
> a written case explaining why the fix is not required. All actions must be
> resolved before QA signs off and moves to Phase 4 (test implementation).

## How to use this file

1. Work through Actions in priority order (P1 before P2).
2. For each Action, either apply the fix or write a justification under
   **Resolution** explaining why the fix is not required.
3. P1 Actions block Phase 4. P2 Actions may be resolved concurrently
   with Phase 4.
4. Update the sign-off checklist at the bottom when each Action is resolved.

---

## Action 1 — P1 · Unused fixture parameter in `test_unknown_kwarg_raises_input_error`

**Priority:** P1
**File:** `tests/test_table_errors.py`, line 70

### What is wrong

`TestTableUnknownConfigKey.test_unknown_kwarg_raises_input_error` declares
`table_example1: Table` as a parameter but never references it in the test body:

```python
def test_unknown_kwarg_raises_input_error(self, table_example1: Table) -> None:
    """Passing an unrecognised config keyword should raise InputError."""
    src = "./tests/data/table_example1.csv"
    with pytest.raises(InputError):
        Table(src, nonexistent_option=True)  # table_example1 is never used
```

This has three concrete problems:

1. **Wasted work.** The `table_example1` fixture is function-scoped.  Every
   invocation of this test triggers a full `Table` construction — file I/O,
   MIPS algorithm, CC1–CC4 search, footnote detection — then discards the
   result.  That is ~50–100 ms of unnecessary work per run.

2. **Misleading.** A reader (or a future QA review) seeing the fixture
   parameter reasonably infers it provides context or shared state.  It does
   not.  The test is entirely self-contained.

3. **Hidden coupling.** The test now has a silent dependency on
   `table_example1.csv` being parseable.  If that fixture ever breaks for
   an unrelated reason, this test will also fail with a confusing error that
   points away from the actual problem under test.

### What a correct fix looks like

Remove `table_example1: Table` from the method signature:

```python
def test_unknown_kwarg_raises_input_error(self) -> None:
    """Passing an unrecognised config keyword should raise InputError."""
    src = "./tests/data/table_example1.csv"
    with pytest.raises(InputError):
        Table(src, nonexistent_option=True)
```

No other changes are needed. The test body is already correct.

### What "no fix required" would need to argue

That the fixture is intentionally present as a pre-condition check — i.e.,
the test is only meaningful if `table_example1.csv` parses successfully first,
and the fixture failure acts as a sentinel for that.  This argument would
require documenting that intent explicitly in the docstring, since it is
not currently visible to readers.

### Resolution

Fixture parameter removed. `test_unknown_kwarg_raises_input_error` now has no
parameters — it is fully self-contained and no longer depends on
`table_example1.csv` being parseable.

---

## Action 2 — P2 · Redundant `try/except TypeError: raise` in `_load_raw_table`

**Priority:** P2
**File:** `src/chemtabextract/table/table.py`, lines 115–118

### What is wrong

`Table._load_raw_table` contains a `try/except` block that catches `TypeError`
and immediately re-raises it without any modification or side-effect:

```python
def _load_raw_table(self) -> np.ndarray:
    try:
        temp = from_any.create_table(self._file_path, self._table_number)
    except TypeError:
        raise  # no-op: catches and immediately re-raises unchanged
    assert isinstance(temp, np.ndarray) and temp.dtype == "<U60"
    ...
```

This pattern is a no-op.  If `create_table` raises `TypeError`, the exception
propagates whether or not the `try/except` is present.  The `assert` and
`ndim` check that follow are only reachable on a clean return from
`create_table`, so they are already unreachable on exception — the `try/except`
provides no protection.

The pattern is a fossil from the old `raw_table` property, where it was
paired with an `else:` clause (the validations lived inside `else`, and the
`try/except TypeError: raise` prevented them running on a failed call).  In
`_load_raw_table` the `else` has been removed but the skeleton remains,
creating a false impression that it is doing something useful (e.g., logging
or transforming the exception).

### What a correct fix looks like

Remove the `try/except` wrapper entirely:

```python
def _load_raw_table(self) -> np.ndarray:
    temp = from_any.create_table(self._file_path, self._table_number)
    assert isinstance(temp, np.ndarray) and temp.dtype == "<U60"
    if temp.ndim == 1:
        msg = "Input table has only one row or column."
        log.critical(msg)
        raise InputError(msg)
    return temp
```

`TypeError` from `create_table` will propagate naturally, as it always has.

### What "no fix required" would need to argue

That the `try/except TypeError: raise` is intentionally kept as a marker for
future developers to add error handling (e.g., logging or wrapping) at that
site, and that a comment to that effect makes this intent clear.  Without such
a comment, the current state is misleading.

### Resolution

`try/except TypeError: raise` block removed from `_load_raw_table`. `TypeError`
from `create_table` now propagates naturally. Docstring updated to note this
explicitly (`Raises: TypeError: Propagated from create_table …`).

---

## Action 3 — P1 · `lxml` is a de-facto runtime dependency but is not declared

**Priority:** P1
**File:** `pyproject.toml`, `[project] dependencies` block;
          `src/chemtabextract/input/from_html.py`, line 124

### What is wrong

`from_html.read_file` and `from_html.read_url` both call:

```python
html_soup = BeautifulSoup(file, features="lxml")
```

`lxml` is hardcoded as the BeautifulSoup parser.  If `lxml` is not installed,
BeautifulSoup raises `bs4.exceptions.FeatureNotFound` immediately — there is
no fallback.  Yet `lxml` does not appear anywhere in `pyproject.toml`.

This means any user or CI environment that installs `chemtabextract` without
`lxml` will get a hard crash the moment they attempt to read an HTML file or
URL, with no hint from the package metadata that `lxml` is required.

This was surfaced during Phase 4 test implementation: all 10 `test_input_from_html`
tests failed with `FeatureNotFound` on a clean venv until `lxml` was added to
the dev dependency group.  The production dependency remains undeclared.

### What a correct fix looks like

**Option A — Declare `lxml` as a core runtime dependency** (simplest):

```toml
[project]
dependencies = [
  "beautifulsoup4>=4.12.0",
  "lxml>=4.9.0",        # required by from_html.py for BeautifulSoup parsing
  ...
]
```

This is correct if HTML input is considered a core feature of the library
(i.e., always available when `chemtabextract` is installed).

**Option B — Move HTML reading into the `[web]` optional extra**:

The `[web]` extra already exists for Selenium.  If HTML parsing is considered
an optional feature, `lxml` (and `beautifulsoup4`) could be moved there.
This is a larger change — it requires gating the `from_html` import behind an
availability check, similar to how Selenium is handled — but it would make the
dependency footprint of the core install lighter.

Either option is acceptable.  The current state (silent runtime crash) is not.

### What "no fix required" would need to argue

That `lxml` is guaranteed to be present in all environments where
`chemtabextract` is used (e.g., it is always installed as a transitive
dependency of another required package).  This argument would need to identify
the specific transitive chain and explain why it is stable across Python
versions and dependency resolution scenarios.

### Resolution

Option A applied. `lxml>=4.9.0` added to `[project] dependencies` in
`pyproject.toml`. The runtime floor is set lower than the dev pin (`>=6.0.2`)
to give users flexibility while ensuring lxml is always present. After `uv sync`
the previously-failing `test_input_from_html` suite (10 tests) now passes,
confirming the fix resolves the `FeatureNotFound` crash.

---

## Backlog Items (no action required before sign-off)

Discovered during review; pre-existing issues out of scope for this milestone.

| Item | File | Risk |
|------|------|------|
| `configure_selenium()` returns `None` for non-Firefox browsers; `read_url` does not check before calling `driver.get()` | `input/from_html.py`, line 197 | Latent `AttributeError` — not triggered in practice since defaults are used, but the code path exists |
| Selenium `driver` is never `quit()`-ed in `read_url` | `input/from_html.py`, ~line 197 | Resource leak if the Selenium path is exercised |
| `assert isinstance(temp, ...) and temp.dtype == "<U60"` uses `assert` for runtime validation | `table/table.py`, line 119 | Assertion is disabled under `python -O`; should be a proper `if/raise` |
| `from_html.py` uses deprecated BS4 method `findAll` (replaced by `find_all` since BS4 4.0.0) | `input/from_html.py`, lines 38 and 54 | 14 deprecation warnings emitted during test run; will become an error in a future BS4 release |

---

## Sign-off Checklist

| Action | Priority | Status | Resolved by |
|--------|----------|--------|-------------|
| Action 1 — Unused fixture in `test_unknown_kwarg_raises_input_error` | P1 | ✅ Resolved | `tests/test_table_errors.py` |
| Action 2 — Redundant `try/except TypeError: raise` in `_load_raw_table` | P2 | ✅ Resolved | `src/chemtabextract/table/table.py` |
| Action 3 — `lxml` undeclared runtime dependency | P1 | ✅ Resolved | `pyproject.toml` |

> **QA sign-off: GRANTED** — 2026-03-17
> All three Actions verified against source. 207/207 tests passing, 8 xfailed.
> Branch coverage 81.29% (gate: 75%). No open findings remain.
