# umbi

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/umbi)](https://pypi.org/project/umbi/)
[![Latest Tag](https://img.shields.io/github/tag/pmc-tools/umbi.svg)](https://github.com/pmc-tools/umbi/tags)
[![Build Status](https://img.shields.io/github/actions/workflow/status/pmc-tools/umbi/test-build.yml)](https://github.com/pmc-tools/umbi/actions)

Library for input/output of annotated transition systems (ATSs) in a *unified Markov binary (UMB)* format. See the [format specification](https://github.com/pmc-tools/umb/) for details.

## Installation:

```bash
pip install umbi
```

## Quick start

A short example where we read a umbfile into an [`ExplicitAts`](umbi/ats/explicit_ats.py) object, modify initial states, and write it back:

```python
import umbi
ats = umbi.ats.read("in.umb")
ats.set_initial_states([ats.num_states - 1])
umbi.ats.write(ats, "out.umb")
```

More examples can be found in the [./examples](./examples) folder.

## API

`umbi` offers multiple levels of abstraction for working with UMB files:

**[`TarFile`](umbi/tar/tar_file.py) and [`TarCoder`](umbi/tar/tar_coder.py)** - low-level access to umbfile contents.

**[`ExplicitUmb`](umbi/umb/explicit_umb.py)** - in-memory representation of a typical umbfile. Attributes are standard Python objects (lists, dicts, dataclasses) providing a deserialized view of the file contents.

**[`ExplicitAts`](umbi/ats/explicit_ats.py)** - format-agnostic abstraction for annotated transition systems (states, transitions, annotations). Recommended for most use cases: easiest to use programmatically and remains stable across UMB format changes.

## CLI

`umbi` provides a basic CLI for umbfile manipulation.

**Options:**
- `--import-umb <path>` - import umbfile as `ExplicitUmb`
- `--import-ats <path>` - import umbfile as `ExplicitAts`
- `--export <path>` - export to umbfile (requires `--import-umb` or `--import-ats`)
- `--log-level <LEVEL>` - set logging level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`

**Example:**
```bash
umbi --import-umb input.umb --export output.umb --log-level DEBUG
```

## Development

(optional) create and activate a python environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Setup

Install development dependencies:

```bash
pip install .[dev]
```

### Testing

Run the test suite with [pytest](https://pytest.org/):

```bash
python -m pytest              # run all tests
python -m pytest tests/tar/   # run specific test directory
python -m pytest -k test_name # run tests matching pattern
```

Current test coverage:
- **binary** - serialization and binary data handling
- **datatypes** - data type definitions and conversions
- **tar** - tarfile I/O and utilities

### Code Quality

Pre-commit hooks automatically run code quality checks before each commit. Configuration: [.pre-commit-config.yaml](.pre-commit-config.yaml)

Set up the hooks with:

```bash
pre-commit install
```

Run hooks manually on all files:

```bash
pre-commit run --all-files
```

Individual tools can be run manually:

**[Ruff](https://github.com/astral-sh/ruff)** -- Code formatting and linting. Config: [pyproject.toml](pyproject.toml) (`[tool.ruff]`)
```bash
ruff check .       # check for issues
ruff check . --fix # check and fix
ruff format .      # format code
```

**[Pyright](https://github.com/microsoft/pyright)** -- Static type checking. Config: [pyproject.toml](pyproject.toml) (`[tool.pyright]`)
```bash
pyright             # check entire project
pyright umbi/       # check specific directory
```

### Release

Dependencies are pinned in the [uv.lock](uv.lock) lockfile for reproducible builds. New versions are published to [PyPI](https://pypi.org/project/umbi/) via the [release workflow](.github/workflows/release.yml). The workflow is triggered automatically when:
- a new version tag is pushed (format: `v*.*.*`)
- the [bump version workflow](.github/workflows/bump.yml) completes successfully (can be run manually via GitHub actions)

The release workflow:
1. updates the [uv.lock](uv.lock) lockfile to reflect any dependency changes
2. builds the distribution packages
3. publishes to PyPI via trusted publishing
4. updates the stable branch pointer to track the latest release
