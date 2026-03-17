## ADDED Requirements

### Requirement: TypeError in create_table carries a single clean message string
`create_table()` in `input/from_any.py` SHALL raise `TypeError` with a single
string argument that includes both the explanation and the invalid input value.
The form `raise TypeError(msg, str(name_key))` (two positional args) SHALL NOT
be used.

#### Scenario: TypeError message is a clean string
- **WHEN** `create_table("")` is called with an unsupported input
- **THEN** `str(err)` on the caught `TypeError` equals a single descriptive
  string (not a repr of a tuple)

### Requirement: Truncation warning emitted when cell values exceed 200 characters
Input parsers (`from_csv`, `from_html`, `from_list`) SHALL emit a
`logging.warning` if any cell value in the parsed table exceeds 200 characters,
indicating that data may have been truncated.

#### Scenario: Warning emitted for long cells
- **WHEN** a CSV, HTML, or list input contains a cell with more than 200
  characters
- **THEN** a warning is logged mentioning the cell length or truncation risk

#### Scenario: No warning for normal-length cells
- **WHEN** all cell values are 200 characters or fewer
- **THEN** no truncation warning is logged

### Requirement: Input parsers use dynamic numpy dtype
`from_csv.read()`, `from_html.makearray()`, and `from_list.read()` SHALL
derive the numpy array dtype from the maximum cell length in the input data.
The fixed `dtype="<U60"` SHALL NOT be used. The derived dtype SHALL be at least
`<U1`.

#### Scenario: Cell values are not truncated
- **WHEN** a table contains a cell value of 100 characters
- **THEN** the numpy array stores all 100 characters without truncation
