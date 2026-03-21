# umbi

Library for input/output of transition systems in a *unified Markov binary (UMB)* format. See the [format specification](https://github.com/pmc-tools/umb/) for details.

## Installation:

(optional) create and activate a python environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install `umbi` via
```bash
pip install umbi
```

## Quick start

Read a umbfile into an `ExplicitAts` object, modify initial states, and write it back:

```python
import umbi
ats : ExplicitAts = umbi.ats.read("in.umb")
ats.set_initial_states([ats.num_states - 1])
umbi.ats.write(ats, "out.umb")
```

More examples can be found in the [./examples](./examples) folder.

## API

`umbi` offers three levels of abstraction for working with UMB files:

**[`TarFile`](umbi/io/tar_file.py) and [`TarCoder`](umbi/io/tar_coder.py)** - Low-level access to tarfile contents.

**[`ExplicitUmb`](umbi/umb/explicit_umb.py)** - In-memory representation of a typical umbfile. Attributes are standard Python objects (lists, dicts, dataclasses) providing a deserialized view of the file contents.

**[`ExplicitAts`](umbi/ats/explicit_ats.py)** - Format-agnostic abstraction for annotated transition systems (states, transitions, annotations). Recommended for most use cases: easiest to use programmatically and remains stable across UMB format changes.

## CLI

`umbi` provides a basic CLI for umbfile manipulation.

**Options:**
- `--import-umb <path>` - Import .umb file as `ExplicitUmb`
- `--import-ats <path>` - Import .umb file as `ExplicitAts`
- `--export <path>` - Export to .umb file (requires `--import-umb` or `--import-ats`)
- `--log-level <LEVEL>` - Set logging level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL`

**Example:**
```bash
umbi --import-umb input.umb --export output.umb --log-level DEBUG
```

## Development

### Setup

Install development dependencies:

```bash
pip install .[dev]
```

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
ruff format .      # format code
ruff check . --fix # check and fix
```

**[Pyright](https://github.com/microsoft/pyright)** -- Static type checking. Config: [pyproject.toml](pyproject.toml) (`[tool.pyright]`)
```bash
pyright             # check entire project
pyright umbi/       # check specific directory
```

#### Lockfiles

Dependencies are pinned in the [uv.lock](uv.lock) lockfile for reproducible builds. To update the lockfile:

```bash
uv lock
```

### Release

New versions are published to PyPI via the [release workflow](.github/workflows/release.yml). The workflow is triggered automatically when:
- A new version tag is pushed (format: `v*.*.*`)
- The [bump version workflow](.github/workflows/bump.yml) completes successfully

Alternatively, the workflow can be triggered manually via GitHub Actions.

The release workflow:
1. Updates the [uv.lock](uv.lock) lockfile to reflect any dependency changes
2. Builds the distribution packages
3. Publishes to PyPI via trusted publishing
4. Updates the stable branch pointer to track the latest release
