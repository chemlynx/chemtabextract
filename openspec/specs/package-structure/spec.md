## ADDED Requirements

### Requirement: Package importable as chemtabextract
The library SHALL be importable as `chemtabextract` from a `src/` layout. All source files SHALL reside under `src/chemtabextract/`. `from tabledataextractor import ...` SHALL raise `ModuleNotFoundError`.

#### Scenario: Top-level import succeeds
- **WHEN** a consumer runs `from chemtabextract import Table, TrivialTable`
- **THEN** both symbols are available and functional

#### Scenario: Old package name is gone
- **WHEN** a consumer runs `from tabledataextractor import Table`
- **THEN** `ModuleNotFoundError` is raised

### Requirement: pyproject.toml is sole build system
The project SHALL use `pyproject.toml` + `uv` as the only build system. `setup.py` SHALL NOT exist in the repository.

#### Scenario: No setup.py
- **WHEN** the repository root is listed
- **THEN** no `setup.py` file exists

#### Scenario: uv sync succeeds
- **WHEN** `uv sync` is run on a clean checkout
- **THEN** the environment resolves and the package is importable

### Requirement: pyproject.toml declares correct metadata
`pyproject.toml` SHALL declare `name = "chemtabextract"`, `version = "0.8.0"`, `requires-python = ">=3.13"`, and a `[tool.commitizen]` section with `version_provider = "pep621"`.

#### Scenario: Package name and version
- **WHEN** `pyproject.toml` is parsed
- **THEN** `project.name` equals `"chemtabextract"` and `project.version` equals `"0.8.0"`

#### Scenario: Commitizen config present
- **WHEN** `pyproject.toml` is parsed
- **THEN** a `[tool.commitizen]` section exists with `version_provider = "pep621"`

### Requirement: All internal imports use chemtabextract namespace
Every `from tabledataextractor.X import Y` or `import tabledataextractor.X` reference in source and test files SHALL be updated to use `chemtabextract`.

#### Scenario: No legacy namespace in source
- **WHEN** the `src/` tree is grepped for `tabledataextractor`
- **THEN** no matches are found

#### Scenario: No legacy namespace in tests
- **WHEN** the `tests/` tree is grepped for `tabledataextractor`
- **THEN** no matches are found
