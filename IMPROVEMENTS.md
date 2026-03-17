# Code Improvement Backlog

Items identified during the QA review that fell outside the top-10 fixes already
applied. Grouped by theme and annotated with suggested priority.

`P1` = should fix soon · `P2` = worth fixing · `P3` = housekeeping / nice-to-have

---

## Error Handling

### E1 — `create_table()` raises `TypeError` with a 2-tuple argument `P2`
**`input/from_any.py`**

```python
raise TypeError(msg, str(name_key))
```

`TypeError` is raised with two positional arguments, so `str(err)` produces
`"('message text', 'input_value')"` rather than a clean message string.
Fix: `raise TypeError(f"{msg}: {name_key!r}")`.

---

### E2 — Pointless `try / except / raise` block in `Table._analyze_table()` `P3`
**`table/table.py`**

```python
try:
    _ = self._cc3
except MIPSError:
    raise
```

This catches `MIPSError` and immediately re-raises it — identical to having no
`try` block at all. Remove it and let `self._cc3` propagate naturally.

---

### E3 — `_set_configs()` calls `_default_configs` property twice per loop iteration `P3`
**`table/table.py`**

```python
configs = self._default_configs          # call 1 — returns a new dict
for key, value in kwargs.items():
    if key in self._default_configs:     # call 2 — returns a *second* new dict
        configs[key] = value
```

`_default_configs` is a property that creates a fresh `dict` on every access, so
`configs` and the membership-test dict are different objects.
Fix: assign once — `defaults = self._default_configs` — and reuse `defaults` for
both the initial assignment and the membership test.

---

## Code Quality

### Q1 — Non-PEP 8 function name `list_as_PrettyTable` `P3`
**`output/print.py`**

Function names must be `lower_case_with_underscores` (PEP 8).
Rename to `list_as_pretty_table` and update the import and call-site in
`table/table.py`.

---

### Q2 — `prefixed_row_or_column()` called twice on the same unchanged input `P2`
**`table/algorithms/_structure.py` lines 166–179**

```python
if prefixed_row_or_column(array):
    row_index, new_row = prefixed_row_or_column(array)   # second full scan
```

The function is an O(n×m) scan. Assign the result once and test its truthiness:

```python
result = prefixed_row_or_column(array)
if result:
    row_index, new_row = result
```

The same pattern repeats for `array.T` two lines below.

---

### Q3 — `Table.transpose()` directly mutates private `History` attributes `P2`
**`table/table.py`, `table/algorithms/_structure.py`**

`History` has read-only public properties but exposes no write interface.
All writes happen by reaching into `_table_transposed`, `_footnotes_copied`, etc.
from outside the class:

```python
self.history._table_transposed = True      # table.py
self._table._history._spanning_cells = True  # _structure.py
```

`History` should expose setter methods or a small update API so callers don't
need to touch private attributes.

---

### Q4 — `Table.configs` property exposes the live mutable `dict` `P2`
**`table/table.py`**

```python
@property
def configs(self):
    return self._configs
```

External code (e.g. `_structure.py`) mutates `table_object.configs["use_title_row"] = False`
directly. Although the mutation is correctly reverted in a `finally` block, this
is a fragile pattern. Consider a dedicated context-manager API for temporary
config overrides, or return a copy from the property.

---

### Q5 — `CellParser.cut()` breaks silently on 1-D arrays `P2`
**`table/parse.py`**

`self.parse()` on a 1-D array yields 2-tuples `(row_index, groups)`.
`CellParser.cut()` then does `result[1]` (treating it as a column index) and
`table[result[:2]]`, both of which produce wrong results or a `TypeError`
without a clear error message. The 1-D path is never tested. Either guard
against 1-D input explicitly or add a test that documents the behaviour.

---

### Q6 — `makearray()` does not fill corner cells when a cell has both `colspan` and `rowspan` `P3`
**`input/from_html.py`**

Cells with *both* attributes have their row-span and column-span cells filled
independently, but the intersection corner cells `(row+r, col+c)` are not
filled. The limitation is undocumented. Add a comment or, better, fix the
nested fill loop.

---

### Q7 — Hard-coded `dtype="<U60"` silently truncates long cell values `P1`
**`input/from_csv.py`, `input/from_html.py`, `input/from_list.py`, and
scattered through `table/algorithms/`**

Every numpy array uses `dtype="<U60"`, capping cell values at 60 Unicode
characters with no warning. Real scientific tables (IUPAC names, footnote text)
routinely exceed this. Options:

* Scan cell lengths at parse time and choose the dtype dynamically
  (`f"<U{max_len}"`)
* Expose a `max_cell_length` config option on `Table`
* At minimum, log a warning when truncation occurs

---

### Q8 — `categorize_header()` is exported but never called `P2`
**`table/algorithms/_categorize.py` and `table/algorithms/__init__.py`**

`categorize_header` is re-exported from the algorithms facade but is never
invoked anywhere in the codebase. It is also entirely untested. Either:

* Remove it and clean up the facade export, or
* Document its intended use and add tests

`sympy.factor_list` is imported solely for this function; removing it would
also trim one dependency.

---

### Q9 — Dead pandas `MultiIndex.labels` compatibility code `P3`
**`output/to_pandas.py` lines 32–46**

`pd.MultiIndex.labels` was removed in pandas 0.24 (2018). The project already
requires `pandas>=0.23.4`; in practice any modern install is ≥ 0.25. The
`hasattr(df.index, "labels")` branch is unreachable dead code. Remove it and
raise the floor in `pyproject.toml` to `pandas>=0.25`.

---

## Architecture

### A1 — `_cc4` and `_cc3` are recomputed on every property access `P2`
**`table/table.py`**

`_cc4` calls `find_cc4()` (an O(n×m) scan) and `_cc3` calls `find_cc3()` on
every access. Both are called multiple times during `_analyze_table()` and by
callers such as `footnotes.py` and `_structure.py`.

A naive `functools.cached_property` or per-call cache breaks the algorithm
because `_cc4` is called with an *intermediate* (pre-spanning-cells) state of
`_pre_cleaned_table` inside `duplicate_spanning_cells()`, then again with the
*final* state afterwards. The correct fix is architectural: pass
`pre_cleaned_table` explicitly as a parameter to `find_cc1_cc2`,
`header_extension_down`, and `find_footnotes` rather than having them read it
off `self`. Once `_pre_cleaned_table` is no longer accessed via `self` inside
those calls, `_cc4` can safely be computed once after the table is fully
prepared and cached as a plain instance attribute.

---

### A2 — Fragile initialisation order in `Table._analyze_table()` `P2`
**`table/table.py`**

The algorithm steps have implicit ordering dependencies that are not documented
and are easy to break:

1. `pre_clean()` must run before `_cc4` is first accessed
2. `duplicate_spanning_cells()` must complete before `find_cc1_cc2()` uses `_cc4`
3. `_cc2` must be set before `_cc3` is accessed

None of these constraints are enforced or documented. Adding inline comments
at each step explaining what prior state is required would make this much safer
to maintain, and is a cheap first step before a deeper refactor.

---

## Type Annotations

### T1 — Public API lacks formal type hints throughout `P2`

Almost no public function uses `def f(x: T) -> R:` syntax. mypy runs with
`no_strict_optional = true` and `ignore_missing_imports = true`, suppressing
most errors. Priority areas to annotate first:

| Location | What to annotate |
|---|---|
| `input/from_any.py` | `create_table()`, `url()`, `html()`, `csv()` |
| `input/from_csv.py` | `read()` |
| `input/from_html.py` | `makearray()`, `read_file()`, `read_url()` |
| `input/from_list.py` | `read()` |
| `table/table.py` | `Table.__init__`, all properties |
| `output/to_csv.py` | `write_to_csv()` — `table` param type |
| `output/to_pandas.py` | all functions |
| `table/parse.py` | all methods (return types) |
| `table/history.py` | all properties |
| `table/footnotes.py` | `Footnote.__init__`, `find_footnotes()` |

Once annotations are in place, consider tightening mypy to
`strict_optional = true` and removing `ignore_missing_imports` for
first-party modules.

---

## Docstrings

### D1 — Several functions have incomplete or incorrect docstrings `P3`

| Location | Issue |
|---|---|
| `input/from_html.py::read_file()` | One-liner; no param docs; `table_number` is 1-indexed but undocumented |
| `output/to_pandas.py::find_multiindex_level()` | Refers to `_build_category_table()` (underscore), actual caller is `build_category_table()` |
| `table/algorithms/_categorize.py::clean_row_header()` | No docstring at all |
| `table/algorithms/_utils.py::duplicate_rows()` / `duplicate_columns()` | `:return: True or False` — these return arrays, not booleans |
| `table/table.py` `TrivialTable.footnotes` / `title_row` / `subtables` | Body is `"""None"""` — not a valid docstring; should read `"""Always returns ``None``."""` with a brief reason |
| `table/history.py::__repr__` | Uses `self._table_transposed` (private attribute) instead of `self.table_transposed` (the public property) |
| `tests/conftest.py` | `table_example2` through `table_example13` fixtures have no docstrings |

---

## Test Coverage

### TC1 — `from_html.py` is almost entirely untested (11% coverage) `P1`

No HTML fixture files exist. `makearray()`, `read_file()`, `read_url()`, and
`configure_selenium()` have zero meaningful test coverage. At minimum, add a
small static `.html` fixture with a simple table and test `read_file()` and
`makearray()` directly.

---

### TC2 — Specific untested behaviours `P2`

| What | Where |
|---|---|
| `CellParser.cut()` and `CellParser.replace()` | `table/parse.py` |
| `StringParser.cut()` (now fixed but still untested) | `table/parse.py` |
| `Table.contains()` | `table/table.py` |
| `History.__repr__()` | `table/history.py` |
| `categorize_header()` | `table/algorithms/_categorize.py` |
| `print_category_table()` | `output/to_pandas.py` |
| `use_max_data_area=True` config path | `table/algorithms/_mips.py` |
| Subtable list where a mid-list subtable fails MIPS (now `continue`s — behaviour is untested) | `table/table.py` |
| `TrivialTable.col_header` / `row_header` with degenerate table sizes | `table/table.py` |
| `Table.transpose()` in isolation (currently only tested via integration) | `table/table.py` |

---

### TC3 — `conftest.py` fixtures are not injected by any test `P3`
**`tests/conftest.py`**

Fixtures `table_example1` through `table_example13` are defined but no test
function uses pytest fixture injection to receive them. Tests instead
instantiate `Table(...)` inline with hardcoded paths, making the fixtures dead
code. Either wire up the fixtures to existing tests or remove them.

---

### TC4 — Coverage threshold is set well below actual coverage `P3`
**`pyproject.toml`**

```toml
[tool.coverage.report]
fail_under = 40
```

Actual branch coverage is ~77%. Raise the threshold to at least 70–75% to
make coverage regressions visible in CI.
