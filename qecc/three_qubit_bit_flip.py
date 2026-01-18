from qiskit import QuantumCircuit


def get_three_qubit_bit_flip_encoding_decoding_circuit() -> QuantumCircuit:
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    return out


def get_three_qubit_bit_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    """
    Error in qubit 0 gives syndrome 01, qubit 1 10, qubit 2 11
    """
    out = QuantumCircuit(5)
    out.cx(0, 4)
    out.cx(1, 3)
    out.cx(2, 3)
    out.cx(2, 4)
    return out
