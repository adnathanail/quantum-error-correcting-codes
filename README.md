# Quantum error correcting codes

[![Tests](https://github.com/adnathanail/quantum-error-correcting-codes/actions/workflows/python-app.yml/badge.svg)](https://github.com/adnathanail/quantum-error-correcting-codes/actions/workflows/python-app.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Install dependencies (including dev)
```shell
uv sync
```

## prek/pre-commit setup (recommended)

[Install prek](https://prek.j178.dev/installation/)

Set up pre-commit hook
```shell
prek install
```

## Manual commands
Run tests
```shell
uv run pytest
```

Run type-checking
```shell
uv run ty check
```

Run linting
```shell
uv run ruff check
```

Run auto-formatting
```shell
uv run ruff format
```
