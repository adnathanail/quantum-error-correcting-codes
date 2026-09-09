"""
Encode a logical qubit with the 9-qubit Shor's code, inject a deliberate X and/or Z error, run
syndrome extraction + correction + decoding, and check the result on the Aer statevector simulator
or the Fermioniq local backend.

Running against Fermioniq requires its local dev server to be running
(`uv run python local_server/server.py` in the Emulator repo) before this script is run.
"""

import argparse
import random
from math import sqrt

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector, random_statevector
from qiskit_aer import AerSimulator

from qecc.nine_qubit_shors_code import (
    apply_nine_qubit_shors_code_bit_flip_correction,
    apply_nine_qubit_shors_code_phase_flip_correction,
    get_nine_qubit_shors_code_decoding_circuit,
    get_nine_qubit_shors_code_encoding_circuit,
    get_nine_qubit_shors_code_syndrome_extraction_circuit,
)
from qecc.utils.fermioniq_local_backend import FermioniqLocalBackend
from qecc.utils.logging import print_blue

STATES = {
    "0": Statevector([1, 0]),
    "1": Statevector([0, 1]),
    "+": Statevector([1 / sqrt(2), 1 / sqrt(2)]),
    "-": Statevector([1 / sqrt(2), -1 / sqrt(2)]),
}

BIT_FLIP_SYNDROMES = (0b000001, 0b000010, 0b000011, 0b000100, 0b001000, 0b001100, 0b010000, 0b100000, 0b110000)


def resolve_error_index(value: str) -> int | None:
    if value == "none":
        return None
    if value == "random":
        return random.randint(0, 8)
    return int(value)


def build_creg_to_qubit_indices(qc: QuantumCircuit) -> dict[ClassicalRegister, list[int]]:
    """
    Map each classical register to the qubit index measured into each of its clbits (ordered by
    clbit index within the register), by inspecting the circuit's measure instructions.
    """
    creg_to_qubit_indices: dict[ClassicalRegister, list[int]] = {creg: [None] * creg.size for creg in qc.cregs}
    for instruction in qc.data:
        if instruction.operation.name != "measure":
            continue
        qubit_index = qc.find_bit(instruction.qubits[0]).index
        clbit = instruction.clbits[0]
        for creg in qc.cregs:
            if clbit in creg:
                creg_to_qubit_indices[creg][creg.index(clbit)] = qubit_index
                break
    return creg_to_qubit_indices


def fermioniq_outcome_to_standard_format(qc: QuantumCircuit, outcome: str) -> str:
    """
    Fermioniq returns one bitstring covering every qubit (MSB = highest qubit index), ignoring our
    circuit's classical registers. Convert it into the space-separated, per-creg format that
    AerSimulator (and Qiskit backends generally) return, so downstream parsing works either way.
    """
    creg_to_qubit_indices = build_creg_to_qubit_indices(qc)
    num_qubits = qc.num_qubits
    parts = ["".join(outcome[num_qubits - 1 - q] for q in reversed(creg_to_qubit_indices[creg])) for creg in reversed(qc.cregs)]
    return " ".join(parts)


def build_circuit(initial_state: Statevector, bit_flip_error_index: int | None, phase_flip_error_index: int | None) -> QuantumCircuit:
    logical = QuantumRegister(9, "logical")
    bit_flip_syndrome = QuantumRegister(6, "bit_flip_syndrome")
    phase_flip_syndrome = QuantumRegister(2, "phase_flip_syndrome")
    bit_flip_creg = ClassicalRegister(6, "bit_flip_syndrome_c")
    phase_flip_creg = ClassicalRegister(2, "phase_flip_syndrome_c")

    qc = QuantumCircuit(logical, bit_flip_syndrome, phase_flip_syndrome, bit_flip_creg, phase_flip_creg)
    qc.initialize(initial_state, [logical[0]])

    qc.compose(get_nine_qubit_shors_code_encoding_circuit(), qubits=logical, inplace=True)
    qc.barrier()

    if bit_flip_error_index is not None:
        qc.x(logical[bit_flip_error_index])
    if phase_flip_error_index is not None:
        qc.z(logical[phase_flip_error_index])
    qc.barrier()

    qc.compose(
        get_nine_qubit_shors_code_syndrome_extraction_circuit(),
        qubits=list(logical) + list(bit_flip_syndrome) + list(phase_flip_syndrome),
        inplace=True,
    )
    qc.barrier()

    # These read qc.cregs[0] and qc.cregs[-1], so they must run before the logical creg is added below
    apply_nine_qubit_shors_code_bit_flip_correction(qc)
    apply_nine_qubit_shors_code_phase_flip_correction(qc)
    qc.barrier()

    qc.compose(get_nine_qubit_shors_code_decoding_circuit(), qubits=logical, inplace=True)

    logical_creg = ClassicalRegister(9, "logical_c")
    qc.add_register(logical_creg)
    qc.measure(logical, logical_creg)

    return qc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", choices=("0", "1", "+", "-", "random"), default="random", help="Logical qubit state to encode")
    parser.add_argument("--bit-flip-error", default="random", help="Qubit index (0-8) to apply a deliberate X error to, 'random', or 'none'")
    parser.add_argument("--phase-flip-error", default="random", help="Qubit index (0-8) to apply a deliberate Z error to, 'random', or 'none'")
    parser.add_argument("--shots", type=int, default=200, help="Number of shots to run on the backend")
    parser.add_argument("--seed", type=int, default=None, help="Random seed, for reproducible runs")
    parser.add_argument("--backend", choices=("aer", "fermioniq"), default="fermioniq", help="Which backend to run the circuit on")
    parser.add_argument("--fermioniq-url", default="http://127.0.0.1:8787", help="URL of the running Fermioniq local dev server (only used with --backend fermioniq)")
    args = parser.parse_args()

    print_blue("Running on " + ("AER state vector simulator" if args.backend == "aer" else "Fermioniq Ava"))
    print()

    if args.seed is not None:
        random.seed(args.seed)

    initial_state = random_statevector(2, seed=args.seed) if args.state == "random" else STATES[args.state]
    bit_flip_error_index = resolve_error_index(args.bit_flip_error)
    phase_flip_error_index = resolve_error_index(args.phase_flip_error)

    print(f"Logical qubit initial state: {initial_state.data}")
    print(f"Deliberate X error on qubit: {bit_flip_error_index}")
    print(f"Deliberate Z error on qubit: {phase_flip_error_index}")

    qc = build_circuit(initial_state, bit_flip_error_index, phase_flip_error_index)

    backend = AerSimulator(method="statevector") if args.backend == "aer" else FermioniqLocalBackend(url=args.fermioniq_url)
    raw_counts = backend.run(qc, shots=args.shots).result().get_counts()

    # AerSimulator (and Qiskit backends generally) already report counts as a space-separated
    # string per classical register. Fermioniq instead returns one bitstring covering every qubit,
    # ignoring our cregs, so normalize it into the same format before doing anything else with it.
    if args.backend == "fermioniq":
        counts: dict[str, int] = {}
        for outcome, count in raw_counts.items():
            standard_outcome = fermioniq_outcome_to_standard_format(qc, outcome)
            counts[standard_outcome] = counts.get(standard_outcome, 0) + count
    else:
        counts = raw_counts

    print(f"\nRan {args.shots} shots on {backend.name}")
    print("\nlogical_c(9)  phase_flip_syndrome_c(2)  bit_flip_syndrome_c(6)  count")
    for outcome, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{outcome:<38} {count}")

    expected_bit_flip_syndrome = format(BIT_FLIP_SYNDROMES[bit_flip_error_index], "06b") if bit_flip_error_index is not None else "0" * 6
    expected_phase_flip_syndrome = format(phase_flip_error_index // 3 + 1, "02b") if phase_flip_error_index is not None else "0" * 2
    expected_syndrome = f"{expected_phase_flip_syndrome} {expected_bit_flip_syndrome}"

    observed_syndromes = {outcome.split(" ", 1)[1] for outcome in counts}
    match = "matches" if observed_syndromes == {expected_syndrome} else "MISMATCH"
    print(f"\nExpected syndrome (phase, bit): {expected_syndrome}")
    print(f"Observed syndrome(s): {', '.join(sorted(observed_syndromes))} — {match}")

    probabilities = initial_state.probabilities()
    print(f"\nExpected logical qubit measurement ratio |0>:|1> = {probabilities[0]:.3f}:{probabilities[1]:.3f}")

    zero_count = sum(count for outcome, count in counts.items() if outcome.split(" ")[0] == "000000000")
    one_count = sum(count for outcome, count in counts.items() if outcome.split(" ")[0] == "000000001")
    other_count = args.shots - zero_count - one_count
    print(f"Observed logical qubit measurement counts: |0>={zero_count}, |1>={one_count}, other (uncorrected)={other_count}")


if __name__ == "__main__":
    main()
