## ADDED Requirements

### Requirement: .pre-commit-config.yaml exists with full hook stack
A `.pre-commit-config.yaml` SHALL exist in the repository root and SHALL include hooks for: `pre-commit-hooks` (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict, debug-statements), `ruff` (lint + format), `mypy`, `bandit`, `vulture`, `xenon`, and a local `pytest-cov` hook.

#### Scenario: Config file present
- **WHEN** the repository root is listed
- **THEN** `.pre-commit-config.yaml` exists

#### Scenario: All required hooks declared
- **WHEN** `.pre-commit-config.yaml` is parsed
- **THEN** repos for pre-commit-hooks, ruff-pre-commit, mirrors-mypy, bandit, vulture, and xenon are present, plus a local pytest-cov hook

### Requirement: pre-commit run --all-files exits 0
After installation and calibration, `pre-commit run --all-files` SHALL exit with code 0 on a clean working tree. All hook findings SHALL have been resolved (fixed, suppressed with documented justification, or whitelisted).

#### Scenario: Clean pre-commit run
- **WHEN** `pre-commit run --all-files` is executed on the repository
- **THEN** exit code is 0 and no unfixed findings are reported

### Requirement: ruff tool config present in pyproject.toml
`pyproject.toml` SHALL contain a `[tool.ruff]` section with `line-length = 100`, `target-version = "py313"`, and a `[tool.ruff.lint]` section selecting `["E", "F", "W", "I"]`.

#### Scenario: Ruff config present
- **WHEN** `pyproject.toml` is parsed
- **THEN** `tool.ruff.line-length` equals `100` and `tool.ruff.lint.select` includes `"E"`, `"F"`, `"W"`, `"I"`

### Requirement: mypy tool config present in pyproject.toml
`pyproject.toml` SHALL contain a `[tool.mypy]` section with `python_version = "3.13"`, `ignore_missing_imports = true`, and a per-module override ignoring errors in `_mips.py`. `_utils.py` is type-clean and does not require an override.

#### Scenario: mypy config present
- **WHEN** `pyproject.toml` is parsed
- **THEN** `tool.mypy.ignore_missing_imports` is `true` and an override for `_mips` exists

### Requirement: bandit tool config present in pyproject.toml
`pyproject.toml` SHALL contain a `[tool.bandit]` section with `exclude_dirs = ["tests"]`.

#### Scenario: bandit config present
- **WHEN** `pyproject.toml` is parsed
- **THEN** `tool.bandit.exclude_dirs` contains `"tests"`

### Requirement: xenon thresholds calibrated against current codebase
The xenon hook SHALL use `--max-absolute B` (or `C` if required by `find_cc1_cc2` complexity). The chosen threshold SHALL be documented in a comment in `.pre-commit-config.yaml` or `pyproject.toml` explaining that `find_cc1_cc2` complexity is known and intentional.

#### Scenario: xenon threshold documented
- **WHEN** `.pre-commit-config.yaml` is reviewed
- **THEN** a comment explains the chosen `--max-absolute` level with reference to MIPS algorithm complexity

#### Scenario: xenon hook passes
- **WHEN** `pre-commit run xenon --all-files` is executed
- **THEN** exit code is 0

### Requirement: CHANGELOG.md initialised at 0.8.0
`CHANGELOG.md` SHALL exist in the repository root, generated via `cz changelog --unreleased-version 0.8.0`, with the `0.8.0` entry edited to describe the fork from `tabledataextractor`.

#### Scenario: CHANGELOG.md present
- **WHEN** the repository root is listed
- **THEN** `CHANGELOG.md` exists

#### Scenario: 0.8.0 entry present
- **WHEN** `CHANGELOG.md` is read
- **THEN** a `## 0.8.0` (or `v0.8.0`) section exists describing the fork from `tabledataextractor`

### Requirement: vulture whitelist covers intentionally exported symbols
A `whitelist.py` (or equivalent vulture config) SHALL exist to suppress false-positive dead code warnings for public API symbols (`Table`, `TrivialTable`, `TDEError`, `InputError`, `MIPSError`) that are exported but unused within the package itself.

#### Scenario: vulture hook passes
- **WHEN** `pre-commit run vulture --all-files` is executed
- **THEN** exit code is 0 with no unresolved findings
