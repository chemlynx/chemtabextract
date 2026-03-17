# QA Developer Actions — improvements-backlog-sweep

> Raised by: QA Engineer review of commit 7b386d4
> Date: 2026-03-17
> Scope: All changes in `feat/improvements-backlog-sweep` — items E1–E3, Q1–Q9,
>        A1–A2, T1, D1 across 13 source files and 5 test files.
>
> For each action below, the developer must either implement the fix or make
> a written case explaining why the fix is not required. All actions must be
> resolved before QA signs off and moves to Phase 4 (test implementation).

## How to use this file

1. Work through Actions in priority order (P1 before P2/P3).
2. For each Action, either apply the fix **or** write a "no fix required"
   justification in the Resolution block.
3. Mark each row in the Sign-off Checklist with ✅ Fixed or ✳️ Justified once
   resolved.
4. P0/P1 actions must be resolved before Phase 4 begins.
   P2/P3 actions may be resolved concurrently with Phase 4.

---

## Action 0 — P0 · `makearray()` crashes with `IndexError` for combined `rowspan+colspan` tables

**Priority:** P0
**File:** `src/chemtabextract/input/from_html.py`, lines 38–46 (`n_cols` calculation) and
line 117 (`skip_index` update)

### What is wrong

The Q6 fix added correct `product()` loop code to fill corner cells when a
cell has both `rowspan` and `colspan`.  **However, writing tests for Q6
revealed two pre-existing defects that make `makearray()` crash or produce
wrong output for the most natural combined-span tables:**

**Defect A — `n_cols` is undersized when the combined cell row is widest.**
The first-pass loop counts visible `<td>/<th>` tags per row without adding
`colspan - 1` for any cell that spans multiple columns:

```python
if len(col_tags) > n_cols:
    n_cols = len(col_tags)   # counts tags, ignores colspan
```

For this table:
```html
<tr><td rowspan="2" colspan="2">A</td><td>B</td></tr>  <!-- 2 tags; logical width = 3 -->
<tr><td>C</td></tr>
```
`n_cols = 2` and `skip_index` is allocated with only 2 entries.  When the
algorithm advances `col_counter` by `col_dim` (which is 2 for the combined
cell) and then tries to place `B` at `col_counter = 2`, it hits
`skip_index[2]` → `IndexError: list index out of range`.

Confirmed by test:
`TestMakearrayCornerCellFill::test_combined_rowspan_colspan_fills_2x2_block` → `IndexError`

**Defect B — `skip_index` not tracked for colspan-spanned columns.**
The skip_index is only updated for `col_counter` (the leftmost column of the
combined cell):

```python
if row_dim[row_dim_counter] > 1:
    this_skip_index[col_counter] = row_dim[row_dim_counter]   # only col_counter
```

The colspan-spanned positions (`col_counter + 1`, `col_counter + 2`, …) are
never added to `skip_index`.  Consequence: when a combined cell is at col 0
(`col_counter = 0`), the next row skips col 0 correctly but then stops at
col 1 (skip_index[1] = 0) and writes its first cell there — overwriting the
corner fill that Q6 just placed.

### What a correct fix looks like

**For Defect A:** The first-pass `n_cols` calculation must sum `colspan` for
each tag:
```python
row_logical_width = sum(int(tag.get("colspan", 1)) for tag in col_tags)
if row_logical_width > n_cols:
    n_cols = row_logical_width
```
The `skip_index` initialisation must use this corrected value.

**For Defect B:** When a cell has both `rowspan` and `colspan`, the
skip_index must be set for ALL spanned columns, not just `col_counter`:
```python
if row_dim[row_dim_counter] > 1:
    for spanned_c in range(col_counter, col_counter + col_dim[col_dim_counter]):
        this_skip_index[spanned_c] = row_dim[row_dim_counter]
```

### What "no fix required" would need to argue

Would need to demonstrate that `makearray()` is never called with HTML
containing a cell that has both attributes simultaneously — which cannot be
argued for a general HTML table parser.

### Resolution

Fixed in `src/chemtabextract/input/from_html.py`:

**Defect A** — The first-pass `n_cols` calculation now sums `colspan` for each
tag using `sum(int(tag.get("colspan", 1)) for tag in col_tags)` instead of
counting raw tags, so `skip_index` is allocated with the correct logical width.

**Defect B** — The `skip_index` update loop now iterates over
`range(col_counter, col_counter + col_dim[col_dim_counter])`, setting the skip
counter for every column the combined cell occupies, not just `col_counter`.

The `xfail` test
`test_combined_rowspan_colspan_without_header_row_crashes` was converted to a
proper passing test (`test_combined_rowspan_colspan_fills_2x2_block`) with
assertions on the full 2×2 block output.

---

## Action 1 — P1 · `CellParser.cut()` 1-D guard has zero test coverage

**Priority:** P1
**File:** `src/chemtabextract/table/parse.py`, lines 88–97

### What is wrong

The Q5 fix added a `ValueError` guard to `CellParser.cut()`:

```python
if table.ndim != 2:
    raise ValueError(
        f"CellParser.cut() requires a 2-D array, got ndim={table.ndim}. "
        "Use a 2-D table as input."
    )
```

The coverage report confirms **lines 88–97 are entirely uncovered** — meaning
neither the guard branch nor the normal execution path of `cut()` is exercised
by any test. The broader method (`cut()`) has no tests at all: `parse()` is
called indirectly for 2-D tables through the table algorithms, but `cut()`
itself has no direct test.

If the guard is accidentally removed or broken, no test will catch the
regression. This defeats the purpose of Q5.

### What a correct fix looks like

Two test cases are needed (both agreed with QA as in-scope for Phase 4):

1. **1-D guard path** — pass a 1-D `np.ndarray` to `cut()` and assert
   `pytest.raises(ValueError)` with the expected message fragment.
2. **2-D happy path** — pass a 2-D array containing a known pattern,
   call `cut()`, and assert the match index and the residual string
   (the pattern cut out of the cell) are correct.

These tests belong in a new `TestCellParserCut` class in a test file for
`table/parse.py` (currently no dedicated test file exists for this module).

### What "no fix required" would need to argue

Would need to demonstrate that `cut()` is unreachable in production
(i.e. no code path calls it) — which is not the case; it is part of the
public `CellParser` API and IS called within the algorithms. "It's tested
indirectly" is not sufficient: indirect coverage through algorithm integration
tests does not exercise the error path.

### Resolution

Already done prior to this QA review. `tests/test_table_parse.py` contains
`TestCellParserCutGuard` (three tests covering the 1-D rejection path and error
message content) and `TestCellParserCut2D` (six tests covering the 2-D happy
path: generator return type, match count, correct indices, absent non-matching
cells, residual string values, and tuple structure). Both classes were present
in the codebase at the time of this review.

---

## Action 2 — P1 · History setter API has no direct unit tests; existing tests bypass setters

**Priority:** P1
**File:** `tests/test_table_history.py`, lines 59–86 and 121

### What is wrong

`TestHistoryPropertySetters` validates properties by setting **private
attributes** directly, not via the new `set_*()` methods added in Q3:

```python
setattr(h, private_attr, True)   # bypasses the new setter API
assert getattr(h, public_prop) is True
```

`test_repr_reflects_updated_flag` also does `h._table_transposed = True`
instead of `h.set_table_transposed(True)`.

As a result, **none of the eight setter methods are tested by a direct unit
test**. They are exercised only as side-effects of integration-level `Table`
construction tests. A typo in a setter body (e.g. setting the wrong backing
attribute) would pass all existing tests.

Additionally, the coverage report confirms `set_title_row_removed` (line 82)
is the only setter never called anywhere — in tests or production code.

### What a correct fix looks like

The existing `TestHistoryPropertySetters` test class should be updated (or
supplemented) so that each test calls the setter method:

```python
h.set_title_row_removed(True)
assert h.title_row_removed is True
```

The `test_repr_reflects_updated_flag` test should similarly use
`h.set_table_transposed(True)`.

For `set_title_row_removed` specifically: the developer should determine
whether this flag is ever intended to be set at runtime (the title row is
currently *labelled*, not physically removed from `pre_cleaned_table`).
If the flag will remain always-`False`, the method docstring should state this
clearly (e.g. *"Reserved; the algorithm currently labels the title row but does
not remove it. This flag may be set in a future iteration."*). If no such
future use is planned, removing the method is the cleaner option — but that is
a design call for the developer to make explicitly.

### What "no fix required" would need to argue

Would need to argue that the integration tests provide sufficient coverage of
every possible setter body, with evidence that each setter is exercised in at
least one integration test path. Given that `set_title_row_removed` is *never*
called, that argument cannot be made for at least one method.

### Resolution

`TestHistorySetterApi` was already present in `tests/test_table_history.py`
with 16 tests exercising all eight `set_*()` methods directly (True-set and
False-reset round-trip for each, plus `repr()` via setter). The one remaining
private-attr bypass — `h._table_transposed = True` in
`test_repr_reflects_updated_flag` — has been changed to
`h.set_table_transposed(True)`.

`set_title_row_removed` is now exercised by `TestHistorySetterApi` and its
intent as reserved/unused by the core algorithm is documented in its docstring
(see Action 5).

---

## Action 3 — P2 · `_override_config` missing return type annotation

**Priority:** P2
**File:** `src/chemtabextract/table/table.py`, line 283

### What is wrong

```python
@contextlib.contextmanager
def _override_config(self, key: str, value: object):  # ← no return type
```

This is new code introduced in Q4. The project convention requires type hints
on all methods. For a `@contextlib.contextmanager`-decorated generator, the
generator function itself should be annotated `-> Iterator[None]`:

```python
from collections.abc import Iterator
...
@contextlib.contextmanager
def _override_config(self, key: str, value: object) -> Iterator[None]:
```

(`collections.abc.Iterator` is already available in Python 3.13 stdlib without
any new import if `from __future__ import annotations` is in scope, but an
explicit import of `Iterator` is needed.)

### What a correct fix looks like

Add `-> Iterator[None]` to the method signature and ensure `Iterator` is
imported from `collections.abc`. No logic change required.

### What "no fix required" would need to argue

Would need to argue that dunder/private methods are exempt from the project's
type-hint convention. The project convention (`CLAUDE.md`: "Type hints: Required
on all functions and methods") does not carve out such an exception.

### Resolution

Added `-> Iterator[None]` to the signature of `_override_config` in
`src/chemtabextract/table/table.py`. `Iterator` is imported from
`collections.abc` (new import line added). No logic change.

---

## Action 4 — P2 · `makearray()` `html_table` parameter has no type annotation

**Priority:** P2
**File:** `src/chemtabextract/input/from_html.py`, line 28

### What is wrong

```python
def makearray(html_table) -> np.ndarray:   # ← html_table is untyped
```

T1 specified type hints for all functions in `from_html.py`. The return type
was added, but the input parameter type was omitted — likely because it
requires importing `Tag` from BeautifulSoup.

### What a correct fix looks like

```python
from bs4 import Tag
...
def makearray(html_table: Tag) -> np.ndarray:
```

QA has confirmed `from bs4 import Tag` is acceptable. `beautifulsoup4` is
already a mandatory runtime dependency, so no new dependency is introduced.

### What "no fix required" would need to argue

Would need to demonstrate that `bs4.Tag` is not importable for type-checking
purposes (e.g. missing type stubs). In practice, `beautifulsoup4` ships type
stubs with the package for Python 3.13.

### Resolution

Added `from bs4 import Tag` import to `src/chemtabextract/input/from_html.py`
and annotated the parameter as `html_table: Tag`. No logic change.

---

## Action 5 — P2 · `set_title_row_removed` is dead code without documentation of intent

**Priority:** P2
**File:** `src/chemtabextract/table/history.py`, lines 80–82

### What is wrong

`set_title_row_removed` was added in Q3 for API consistency, but it has
**no call site anywhere in the codebase** (confirmed by exhaustive grep). The
backing flag `_title_row_removed` is never set to `True` in production code,
meaning `history.title_row_removed` is always `False` at runtime.

The intent is unclear. Two interpretations are plausible:
- The title row is labelled (as `"TableTitle"`) but *not physically removed*
  from `pre_cleaned_table`, so the flag correctly remains `False` and the
  setter is correctly unused.
- The setter was intended to be wired up somewhere and was missed.

Without a code comment or docstring clarifying this, the method looks like
a bug to any future reader.

### What a correct fix looks like

**Option A (if "never called" is intentional):** Add a note to the
`set_title_row_removed` docstring, e.g.:
```python
def set_title_row_removed(self, value: bool) -> None:
    """Set the ``title_row_removed`` flag.

    Note:
        Currently never called by the core algorithm — the title row is
        labelled as ``"TableTitle"`` but not excised from
        ``pre_cleaned_table``. Reserved for future use.
    """
    self._title_row_removed = value
```

**Option B (if the setter is genuinely unneeded):** Remove
`set_title_row_removed`, `_title_row_removed`, and `title_row_removed` from
`History` entirely.

The developer must make this call explicitly.

### What "no fix required" would need to argue

Would need to provide the same intent clarification in a written comment here,
confirming that the setter is intentionally unused and explaining why.

### Resolution

**Option A chosen.** The `set_title_row_removed` docstring in
`src/chemtabextract/table/history.py` now documents that this method is
currently never called by the core algorithm — the title row is labelled as
`"TableTitle"` but not physically removed from `pre_cleaned_table`. The method
is retained as reserved for future use.

---

## Action 6 — P3 · `_set_configs` uses alias assignment instead of `.copy()`

**Priority:** P3
**File:** `src/chemtabextract/table/table.py`, lines 512–514

### What is wrong

```python
defaults = self._default_configs  # access once; property creates a new dict each time
configs = defaults                 # same object — modifying configs also modifies defaults
for key, value in kwargs.items():
    if key in defaults:
        configs[key] = value
```

`configs = defaults` makes them the **same object**. The code is functionally
correct today because `_default_configs` is a plain property that returns a
fresh `dict` on every call — so `defaults` is an independent local dict. But
the alias is non-obvious: a reader must know this property semantics to see
why `configs[key] = value` does not corrupt any persistent defaults.

If `_default_configs` were ever refactored to return a cached object, this
code would silently mutate the cache.

### What a correct fix looks like

```python
defaults = self._default_configs
configs = defaults.copy()        # explicit copy — intent is now obvious
for key, value in kwargs.items():
    if key in defaults:
        configs[key] = value
```

### What "no fix required" would need to argue

That the existing comment (`# access once; property creates a new dict each time`)
is sufficient documentation and the `.copy()` is unnecessary overhead. This
is a defensible position for a P3 item — resolve with a written statement here
if you choose not to fix.

### Resolution

Fixed. `configs = defaults` changed to `configs = defaults.copy()` in
`_set_configs` in `src/chemtabextract/table/table.py`. The accompanying comment
("`# access once; property creates a new dict each time`") was removed — the
explicit `.copy()` makes the intent self-evident without relying on knowledge
of the property's implementation.

---

## Backlog Items (no action required before sign-off)

These are pre-existing issues discovered during the review. They do not block
Phase 4 but should be tracked.

| Item | Location | Suggested Priority |
|---|---|---|
| Coverage gate at 75% when actual coverage is 82.68% — threshold should be ratcheted up (TC4 in IMPROVEMENTS.md) | `pyproject.toml` line 60 | P3 |
| `conftest.py` fixtures `table_example1–13` defined but never injected by any test (TC3 in IMPROVEMENTS.md) | `tests/conftest.py` | P3 |
| `findAll` (deprecated since BeautifulSoup 4.0.0) should be `find_all` — generates 14 deprecation warnings per test run | `src/chemtabextract/input/from_html.py` lines 41, 57 | P3 |

---

## Sign-off Checklist

| Action | Priority | Status | Resolved by |
|---|---|---|---|
| Action 0 — `makearray()` IndexError on combined rowspan+colspan | P0 | ✅ Fixed | Fix `n_cols` (sum colspan) + fix `skip_index` (all spanned cols); xfail test converted to passing assertion |
| Action 1 — `CellParser.cut()` guard untested | P1 | ✅ Fixed | `TestCellParserCutGuard` + `TestCellParserCut2D` already present in `test_table_parse.py` |
| Action 2 — History setter API untested; private-attr bypass in tests | P1 | ✅ Fixed | `TestHistorySetterApi` present; `test_repr_reflects_updated_flag` updated to use `set_table_transposed()` |
| Action 3 — `_override_config` missing return type | P2 | ✅ Fixed | `-> Iterator[None]` added; `Iterator` imported from `collections.abc` |
| Action 4 — `makearray()` `html_table` param untyped | P2 | ✅ Fixed | `from bs4 import Tag`; parameter annotated `html_table: Tag` |
| Action 5 — `set_title_row_removed` dead code undocumented | P2 | ✅ Fixed | Option A: docstring documents reserved/unused status |
| Action 6 — `_set_configs` alias without `.copy()` | P3 | ✅ Fixed | `configs = defaults.copy()` |

> QA sign-off: All Actions resolved. Suite: 263 passed, 5 xfailed, 0 failures.
