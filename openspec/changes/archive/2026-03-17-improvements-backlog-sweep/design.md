## Context

`IMPROVEMENTS.md` was produced by QA review of the `chemtabextract-modernisation`
work. It contains 16 developer-owned issues (E1–E3, Q1–Q9, A1–A2, T1, D1) plus
several QA-owned test-coverage items (TC1–TC4, which are out of scope here).
All issues are in-tree; no new external dependencies are introduced.

## Goals / Non-Goals

**Goals:**
- Fix every developer-owned correctness, quality, and architecture issue in
  `IMPROVEMENTS.md`
- Add type hints to all public API listed under T1
- Fix all docstring defects listed under D1
- Keep the codebase green (tests pass, ruff/mypy clean) after every commit

**Non-Goals:**
- Addressing TC1–TC4 (test-coverage gaps) — those are for QA
- Introducing new features or changing public algorithm behaviour
- Refactoring the MIPS algorithm itself (`_mips.py` is frozen)

## Decisions

### Q3 — History setter API

`History` currently has read-only public properties but no write interface.
External code (in `table.py` and `_structure.py`) reaches into private
attributes directly.

**Decision:** Add explicit `set_<flag>(value: bool)` setter methods to
`History`, one per flag. This is the simplest change that removes the private
attribute access without altering the public property API.

Considered: `@property.setter` decorators or a single `update(**kwargs)` method.
Setters are equally clean; `update()` is more flexible but obscures individual
flag names at call-sites. Chose per-flag setters for clarity.

### Q4 — `Table.configs` mutation

`_structure.py::duplicate_spanning_cells` currently mutates `table_object.configs`
directly to temporarily disable `use_title_row`, restoring it in a `finally` block.
This works only because `configs` returns the live dict today.

**Decision:** Add a `Table._override_config(key, value)` context manager that
temporarily sets a config value on `self._configs` and restores it on exit.
Update `duplicate_spanning_cells` to use it. Then change the `configs` property
to return `self._configs.copy()` so external callers cannot mutate live state.

This approach is strictly backwards-compatible: all internal code is migrated to
the context manager; the public property now returns an immutable snapshot.

### Q5 — `CellParser.cut()` on 1-D arrays

`CellParser.parse()` on 1-D arrays yields 2-tuples `(row_index, groups)`.
`cut()` then does `result[1]` (which gives `groups`) and `table[result[:2]]`
(a 2-element index on a 1-D array — wrong).

**Decision:** Raise a clear `ValueError` at the top of `cut()` if
`table.ndim != 2`. Document this constraint in the docstring.  The 1-D path is
an edge-case with no current callers; making it explicit is safer than silent
wrong results.

### Q7 — Dynamic numpy dtype

Hard-coded `dtype="<U60"` silently truncates cells longer than 60 characters.

**Decision:** In each parser (`from_csv.py`, `from_html.py`, `from_list.py`),
scan the raw cell strings to compute the maximum length, then use
`f"<U{max(max_len, 1)}"` as the dtype. Emit a `logging.warning` if any cell is
longer than 200 characters (a reasonable sentinel for unexpectedly large data).

Considered: a `max_cell_length` config option. Rejected for this pass because it
requires plumbing the option through the `create_table` call chain. The dynamic
scan is O(n×m) but is negligible relative to I/O and MIPS.

### A1 — `_cc4` / `_cc3` caching

`_cc4` and `_cc3` are properties that invoke O(n×m) scans on every access.
`_analyze_table()` calls `_cc4` several times during the pipeline through
different intermediate states, which makes naive `cached_property` incorrect.

**Decision (incremental):** After `_analyze_table()` completes, assign the
final values of `_cc4` and `_cc3` as plain instance attributes
(`self.__cc4_cache` / `self.__cc3_cache`). The properties check for the cache
first and compute lazily if not yet set. On the next `_analyze_table()` call
(e.g. `transpose()`), the caches are cleared.

This is the safe incremental step. The full architectural fix (pass
`pre_cleaned_table` as an explicit argument) is acknowledged in A2 comments
but deferred to a later change because it touches the frozen `_mips.py`
function signatures.

### Q8 — Remove `categorize_header`

`categorize_header` is unused, untested, and the sole reason `sympy` is a
runtime dependency.

**Decision:** Remove the function from `_categorize.py` and its re-export from
`algorithms/__init__.py`. Remove `sympy` from `pyproject.toml` dependencies.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| `configs` copy breaks an undiscovered internal caller | Grepped: only `duplicate_spanning_cells` mutates `configs`; all others read only. Context manager covers it. |
| Dynamic dtype widens arrays; small memory increase | Arrays are short-lived in-process objects; negligible. |
| Removing `sympy` is a breaking change for downstream code using `categorize_header` | Function is undocumented and untested; no public contract exists. Warning added to CHANGELOG. |
| A1 cache-clearing on transpose — `_analyze_table` is called from `__init__` and `transpose()`; both should clear | Explicitly clear `__cc4_cache`/`__cc3_cache` at the start of `_analyze_table`. |

## Migration Plan

No migrations needed. Changes are internal. The pandas floor raise
(`>=0.23.4` → `>=0.25`) is safe given the project already requires Python 3.13.

## Open Questions

None — all decisions above are self-contained and can proceed to implementation.
