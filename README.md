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

### Code Quality

This project uses `pre-commit` hooks (configured in [.pre-commit-config.yaml](.pre-commit-config.yaml)) that automatically run code quality checks and update the lockfile before each commit. These hooks enforce consistent code formatting and type safety across the codebase. Set up the hooks with:

```bash
pre-commit install
```

Run hooks manually on all files:

```bash
pre-commit run --all-files
```

Individual tools can be run manually:

**[Ruff](https://github.com/astral-sh/ruff)** — Code formatting and linting. Config: [pyproject.toml](pyproject.toml) (`[tool.ruff]`)
```bash
ruff check .       # check for issues
ruff format .      # format code
ruff check . --fix # check and fix
```

**[Pyright](https://github.com/microsoft/pyright)** — Static type checking. Config: [pyproject.toml](pyproject.toml) (`[tool.pyright]`)
```bash
pyright             # check entire project
pyright umbi/       # check specific directory
```

#### Lockfiles

Dependencies are pinned in the [uv.lock](uv.lock) lockfile for reproducible builds. The lockfile is automatically updated via pre-commit hooks when [pyproject.toml](pyproject.toml) changes. To manually update:

```bash
uv lock
```
