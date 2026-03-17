## 1. Error Handling Fixes

- [x] 1.1 Fix `create_table()` TypeError: replace two-arg `raise TypeError(msg, str(name_key))` with `raise TypeError(f"{msg}: {name_key!r}")` in both branches of `input/from_any.py`
- [x] 1.2 Remove pointless `try/except MIPSError: raise` passthrough block in `Table._analyze_table()` in `table/table.py`
- [x] 1.3 Fix `_set_configs()` double property access: assign `self._default_configs` once to a local variable and reuse it for both the copy and the membership test

## 2. History Setter API (Q3, D1 partial)

- [x] 2.1 Add `set_<flag>(value: bool)` setter methods to `History` for all eight flags (`set_title_row_removed`, `set_prefixing_performed`, `set_prefixed_rows`, `set_footnotes_copied`, `set_spanning_cells_extended`, `set_header_extended_up`, `set_header_extended_down`, `set_table_transposed`)
- [x] 2.2 Fix `History.__repr__` to use `self.table_transposed` (public property) instead of `self._table_transposed`
- [x] 2.3 Update all callers in `table/table.py` to use setter methods instead of `self.history._<attr> = value`
- [x] 2.4 Update all callers in `table/algorithms/_structure.py` to use setter methods instead of `table_object.history._<attr> = value`

## 3. Table.configs Protection + Override Context Manager (Q4)

- [x] 3.1 Add `Table._override_config(key: str, value: object)` context manager to `table/table.py` that temporarily sets `self._configs[key]` and restores on exit
- [x] 3.2 Update `duplicate_spanning_cells` in `_structure.py` to use `table_object._override_config("use_title_row", False)` instead of direct dict mutation
- [x] 3.3 Change `Table.configs` property to return `self._configs.copy()` instead of the live dict

## 4. Code Quality Fixes (Q1, Q2, Q5, Q6)

- [x] 4.1 Rename `list_as_PrettyTable` → `list_as_pretty_table` in `output/print.py` and update both call-sites in `table/table.py`
- [x] 4.2 Cache `prefixed_row_or_column()` result in `_structure.py`: assign once, test the cached value — fix both the `array` and `array.T` call-sites
- [x] 4.3 Add `ValueError` guard at the top of `CellParser.cut()` in `table/parse.py` for `table.ndim != 2`; update the docstring to document the constraint
- [x] 4.4 Fix `makearray()` in `input/from_html.py` to fill corner cells for combined `colspan+rowspan`: add inner loop `for r, c in product(...)` to populate intersection cells

## 5. Dynamic dtype + Truncation Warning (Q7)

- [x] 5.1 Update `from_csv.read()` to compute max cell length and use `f"<U{max(max_len, 1)}"` as the dtype; warn if any cell exceeds 200 chars
- [x] 5.2 Update `from_html.makearray()` to use dynamic dtype derived from max cell length; warn if any cell exceeds 200 chars
- [x] 5.3 Update `from_list.read()` to compute max cell length and use dynamic dtype; warn if any cell exceeds 200 chars
- [x] 5.4 Update `Table._load_raw_table()` assertion in `table/table.py` to not hard-code `"<U60"` (remove or relax the dtype assertion)

## 6. Remove categorize_header + sympy (Q8)

- [x] 6.1 Delete `categorize_header` function and `from sympy import Symbol, factor_list` import from `table/algorithms/_categorize.py`
- [x] 6.2 Remove `categorize_header` re-export from `table/algorithms/__init__.py`
- [x] 6.3 Remove `sympy` from the `dependencies` list in `pyproject.toml`

## 7. Remove Dead Code (Q9)

- [x] 7.1 Remove `hasattr(df.index, "labels")` and `hasattr(df.columns, "labels")` compatibility branches from `output/to_pandas.py`
- [x] 7.2 Raise pandas floor in `pyproject.toml` to `pandas>=0.25`
- [x] 7.3 Update `find_multiindex_level` docstring to remove reference to `_build_category_table()` (fix D1 item for this function)

## 8. Architecture: _cc4/_cc3 Caching + Ordering Comments (A1, A2)

- [x] 8.1 Add `__cc4_cache` and `__cc3_cache` instance attribute slots; clear them at the start of `_analyze_table()`
- [x] 8.2 After `_analyze_table()` completes, populate `__cc4_cache` and `__cc3_cache` with the final values
- [x] 8.3 Update `Table._cc4` and `Table._cc3` properties to return cached values when available
- [x] 8.4 Add ordering-constraint inline comments to `Table._analyze_table()` documenting the three prerequisite dependencies (pre_clean before _cc4; duplicate_spanning_cells before find_cc1_cc2; _cc2 set before _cc3)

## 9. Type Hints (T1)

- [x] 9.1 Add type hints to all public functions in `input/from_any.py`: `url()`, `html()`, `csv()`, `create_table()`
- [x] 9.2 Add type hints to `input/from_csv.read()`, `input/from_html.read_file()`, `input/from_html.makearray()`, `input/from_html.read_url()`, `input/from_list.read()`
- [x] 9.3 Add type hints to `Table.__init__`, all `Table` properties, and `TrivialTable.__init__` in `table/table.py`
- [x] 9.4 Add type hints to `output/to_csv.write_to_csv()`, all functions in `output/to_pandas.py`
- [x] 9.5 Add type hints to all methods in `table/parse.py` (return types for `CellParser` and `StringParser`)
- [x] 9.6 Add type hints to all properties in `table/history.py` and `table/footnotes.py`

## 10. Docstring Fixes (D1)

- [x] 10.1 Expand `input/from_html.py::read_file()` docstring: add `Args:` and `Returns:` sections; document `table_number` as 1-indexed
- [x] 10.2 Add `clean_row_header()` docstring in `table/algorithms/_categorize.py`
- [x] 10.3 Fix `_utils.py::duplicate_rows()` and `duplicate_columns()` docstrings: return type is `np.ndarray`, not `True or False`
- [x] 10.4 Fix `TrivialTable.footnotes`, `TrivialTable.title_row`, `TrivialTable.subtables` docstrings from `"""None"""` to `"""Always returns ``None``."""` with a brief reason
