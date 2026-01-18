from qiskit import QuantumCircuit


def get_three_qubit_bit_flip_encoding_decoding_circuit() -> QuantumCircuit:
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    return out


def get_three_qubit_bit_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    out = QuantumCircuit(5)
    out.cx(0, 3)
    out.cx(2, 3)
    out.cx(1, 4)
    out.cx(2, 4)
    return out
