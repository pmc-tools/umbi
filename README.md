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

### Installing Development Tools
Run the following command to install all development dependencies:

```bash
pip install .[dev]
```

This will install tools for testing, linting, and other development tasks.

### Setting Up Pre-Commit Hooks
To ensure code quality and consistency, this repository uses `pre-commit` hooks that automatically run code formatting and linting ([Ruff](https://github.com/astral-sh/ruff)), and type checking ([Pyright](https://github.com/microsoft/pyright)) before each commit. Developers should set up the hooks by running the following command:

```bash
pre-commit install
```

This will configure `pre-commit` to automatically run checks before each commit. To manually run the hooks on all files, use:

```bash
pre-commit run --all-files
```

The following sections describe how to run Ruff and Pyright individually.

### Code Formatting and Linting with Ruff

This project uses [Ruff](https://github.com/astral-sh/ruff) for fast linting and formatting. Configuration can be found in `[tool.ruff]` section of `pyproject.toml`.

**Check code for linting issues:**
```bash
ruff check .
```

**Format code automatically:**
```bash
ruff format .
```

**Check and fix issues in one command:**
```bash
ruff check . --fix
```

### Type Checking with Pyright

This project uses [Pyright](https://github.com/microsoft/pyright) for static type checking. Configuration can be found in `[tool.pyright]` section of `pyproject.toml`.

**Run type checker on the entire project:**
```bash
pyright
```

**Run type checker on a specific directory:**
```bash
pyright umbi/
```

Pyright is configured via `pyrightconfig.json` in the project root. Type hints should be added throughout the codebase to ensure comprehensive type coverage.



