## ADDED Requirements

### Requirement: History exposes setter methods for all flags
`History` SHALL provide a public setter method for each flag it tracks. Callers
SHALL use these methods instead of directly accessing private attributes. No
caller outside `History` SHALL reference `_title_row_removed`,
`_prefixing_performed`, `_prefixed_rows`, `_footnotes_copied`,
`_spanning_cells_extended`, `_header_extended_up`, `_header_extended_down`, or
`_table_transposed` directly.

#### Scenario: Setter method exists for every flag
- **WHEN** a `History` instance is created
- **THEN** it has methods `set_title_row_removed`, `set_prefixing_performed`,
  `set_prefixed_rows`, `set_footnotes_copied`, `set_spanning_cells_extended`,
  `set_header_extended_up`, `set_header_extended_down`, and
  `set_table_transposed`, each accepting a single `bool` argument

#### Scenario: Setter updates the corresponding property
- **WHEN** `history.set_table_transposed(True)` is called
- **THEN** `history.table_transposed` returns `True`

#### Scenario: No private attribute access from table.py or _structure.py
- **WHEN** `src/chemtabextract/table/table.py` and
  `src/chemtabextract/table/algorithms/_structure.py` are grepped for
  `history._` (underscore prefix on history attributes)
- **THEN** no matches are found

### Requirement: History.__repr__ uses public properties only
`History.__repr__` SHALL reference `self.table_transposed` (the public
property) instead of `self._table_transposed` (the private attribute).

#### Scenario: repr uses public property
- **WHEN** `History.__repr__` source is inspected
- **THEN** it does not reference `self._table_transposed`
