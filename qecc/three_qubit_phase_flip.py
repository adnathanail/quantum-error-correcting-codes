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
