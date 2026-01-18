# CLAUDE.md

## Project Overview

Implementing quantum error-correcting codes in Qiskit. The `qecc` package is structured as an importable library, with separate `tests/` and `scripts/` directories.

## Commands

**Do not run commands - ask me to run them for you**

- `uv run pytest` - run tests
- `uv run scripts/generate_circuits.py` - generate circuit diagrams to `imgs/`
- `uv run ruff check` - lint
- `uv run ruff format` - format

## Architecture

### Library (`qecc/`)

Each error-correcting code has:
- **Encoding circuit** - transforms logical qubits into encoded form
- **Decoding circuit** - reverses encoding (may be same circuit if self-inverse)
- **Syndrome extraction circuit** - detects errors without collapsing the encoded state
- **Correction function** - applies conditional gates based on syndrome measurement

### Codes Implemented

| Code | Protects Against | Encoding | Correction Gate |
|------|------------------|----------|-----------------|
| 3-qubit bit flip | X errors | \|0⟩→\|000⟩, \|1⟩→\|111⟩ | X |
| 3-qubit phase flip | Z errors | \|0⟩→\|+++⟩, \|1⟩→\|---⟩ | Z |

Key difference: bit flip encoding/decoding uses the same circuit (CNOTs are self-inverse), while phase flip needs separate encode/decode circuits (involves Hadamards).

### Tests (`tests/`)

`tests/utils.py` contains:
- `QuantumCircuitTest` - base class with measurement helpers
- `ThreeQubitEncodingQuantumCircuitTest` - adds syndrome constants
- `_check_results_ratio()` - generic measurement verification with statistical tolerance
- `hadamard_basis` parameter - applies H gates before measurement (useful for phase flip code verification)

Test classes use a non-`Test` prefixed base class to avoid pytest running inherited tests multiple times.

## Qiskit Notes

- Measurement strings are little-endian (rightmost bit = qubit 0)
- Access classical registers via `qc.cregs[0]`
- Circuit composition: `qc.compose(other, qubits=(0,1,2), inplace=True)`
- Conditional gates: `with qc.if_test((clreg, 0b01)): qc.x(0)`
