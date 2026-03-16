## ADDED Requirements

### Requirement: Django is not a dependency
The `django` package SHALL NOT appear in `[project.dependencies]` or any runtime dependency group. The library SHALL install and run without Django present.

#### Scenario: uv sync without Django
- **WHEN** `uv sync` is run
- **THEN** Django is not installed in the environment

#### Scenario: URL validation works without Django
- **WHEN** `from chemtabextract.input.from_any import url` is called with valid and invalid URL strings
- **THEN** correct boolean results are returned with no Django import

### Requirement: URL validation uses stdlib urllib.parse
The `url()` function in `input/from_any.py` SHALL use `urllib.parse.urlparse` to detect valid URLs. It SHALL return `True` for `http://`, `https://`, and `ftp://` URLs with a non-empty netloc, and `False` for all other strings.

#### Scenario: Valid HTTP URL accepted
- **WHEN** `url("http://example.com/table.html")` is called
- **THEN** it returns `True`

#### Scenario: Valid HTTPS URL accepted
- **WHEN** `url("https://example.com/table.html")` is called
- **THEN** it returns `True`

#### Scenario: Valid FTP URL accepted
- **WHEN** `url("ftp://example.com/table.csv")` is called
- **THEN** it returns `True`

#### Scenario: Bare hostname rejected
- **WHEN** `url("example.com/table.html")` is called
- **THEN** it returns `False`

#### Scenario: Non-URL string rejected
- **WHEN** `url("not-a-url")` is called
- **THEN** it returns `False`

#### Scenario: Empty string rejected
- **WHEN** `url("")` is called
- **THEN** it returns `False`

#### Scenario: Local path rejected
- **WHEN** `url("/local/path/table.csv")` is called
- **THEN** it returns `False`

#### Scenario: file:// scheme rejected
- **WHEN** `url("file:///etc/passwd")` is called
- **THEN** it returns `False`

### Requirement: selenium is an optional dependency
`selenium` SHALL NOT appear in `[project.dependencies]`. It SHALL be declared under `[project.optional-dependencies]` as `web = ["selenium>=3.141.0"]`.

#### Scenario: Optional extra declared
- **WHEN** `pyproject.toml` is parsed
- **THEN** `project.optional-dependencies.web` contains a selenium entry

#### Scenario: Import without selenium raises clear error
- **WHEN** selenium is not installed and a JS-rendered URL fetch is attempted
- **THEN** `InputError` is raised with a message including `chemtabextract[web]`

### Requirement: Dev dependencies are in dependency-groups
All development tooling (pytest, pytest-cov, pre-commit, ruff, mypy, bandit, vulture, xenon, commitizen) SHALL be declared in `[dependency-groups] dev`, not in `[project.dependencies]`.

#### Scenario: Dev tools not in runtime deps
- **WHEN** `pyproject.toml` `[project.dependencies]` is parsed
- **THEN** none of pytest, ruff, mypy, bandit, vulture, xenon, commitizen appear

#### Scenario: Dev group present
- **WHEN** `pyproject.toml` is parsed
- **THEN** a `[dependency-groups]` section with a `dev` key exists

### Requirement: Doc dependencies are in dependency-groups
All documentation tooling (sphinx, m2r, nbsphinx, nbsphinx-link, jinja2, ipykernel) SHALL be declared in `[dependency-groups] docs`, not in `[project.dependencies]`.

#### Scenario: Doc tools not in runtime deps
- **WHEN** `pyproject.toml` `[project.dependencies]` is parsed
- **THEN** none of sphinx, m2r, nbsphinx appear

#### Scenario: Docs group present
- **WHEN** `pyproject.toml` is parsed
- **THEN** a `[dependency-groups]` section with a `docs` key exists
