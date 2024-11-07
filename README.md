# Python template repository

Using:

- `poetry` for dependency management and packaging.
- `pytest` for testing.
- `ruff` for formatting.
- `mypy` for static type checking.
- `pre-commit` for code quality.

**It includes a basic structure for a Poetry project.**

```bash
.
├── src/
│   └── __init__.py
│   └── __main__.py
│   └── py.typed
├── tests/
│   └── test.py
├── pyproject.toml
├── poetry.lock
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── .dockerignore
```

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run app
```

## Testing

```bash
pytest -c pyproject.toml
```

## Formatting

```bash
poetry run poe format-code
```

## Pre-commit

```bash
poetry shell
pre-commit install
```
