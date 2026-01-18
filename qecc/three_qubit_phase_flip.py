"""
Reference https://quantum.cloud.ibm.com/learning/en/courses/foundations-of-quantum-error-correction/correcting-quantum-errors/repetition-codes#phase-flip-errors
"""

from qiskit import QuantumCircuit


def get_three_qubit_phase_flip_encoding_circuit() -> QuantumCircuit:
    """
    Encode |0> as (|+++>) and |1> as (|--->)
    """
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    out.h(0)
    out.h(1)
    out.h(2)
    return out


def get_three_qubit_phase_flip_decoding_circuit() -> QuantumCircuit:
    out = QuantumCircuit(3)
    out.h(0)
    out.h(1)
    out.h(2)
    out.cx(0, 1)
    out.cx(0, 2)
    return out


def get_three_qubit_phase_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    """
    Error in qubit 0 gives syndrome 01, qubit 1 10, qubit 2 11
    """
    out = QuantumCircuit(5)
    out.h(3)
    out.h(4)
    out.cx(3, 0)
    out.cx(4, 1)
    out.cx(3, 2)
    out.cx(4, 2)
    out.h(3)
    out.h(4)
    return out
