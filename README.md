# Quantum error correcting codes

[![Run tests](https://github.com/adnathanail/quantum-error-correcting-codes/actions/workflows/ci.yml/badge.svg)](https://github.com/adnathanail/quantum-error-correcting-codes/actions/workflows/ci.yml)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

_I have used Claude code to assist with boilerplate, some aspects of writing automated tests, and debugging. All circuits have been implemented by hand._

Install dependencies (including dev)
```shell
uv sync
```

## Generate images of circuits

```shell
uv run scripts/gen_imgs.py
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
