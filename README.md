# umbi

Library for input/output of transition systems in a *unified Markov binary (UMB)* format.

## Installation:

(optional) create and activate a python environment:

```
$ python -m venv venv
$ source venv/bin/activate
```

Install `umbi` via
```
(venv) $ pip install umbi
```

## Running umbi

Examples:
```
(venv) $ umbi --import-umb /path/to/input.umb
(venv) $ umbi --import-umb /path/to/input.umb --export-umb /path/to/output.umb
(venv) $ umbi --import-umb /path/to/input.umb --export-umb /path/to/output.umb --log-level=DEBUG
```

## Development

### Setup

Install development dependencies:

```bash
pip install .[dev]
```

Configure pre-commit hooks to automatically run code quality checks before each commit:

```bash
pre-commit install
```

Run hooks manually on all files:

```bash
pre-commit run --all-files
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting, and [Pyright](https://github.com/microsoft/pyright) for type checking. Configuration is in `pyproject.toml`.

**Ruff:**
```bash
ruff check .       # check for issues
ruff format .      # format code
ruff check . --fix # check and fix
```

**Pyright:**
```bash
pyright             # check entire project
pyright umbi/       # check specific directory
```

### Lockfiles

Dependencies are pinned using `uv.lock` for reproducible builds. Update lockfiles when `pyproject.toml` changes:

```bash
uv lock
```

Commit the updated lockfile along with `pyproject.toml` changes.
