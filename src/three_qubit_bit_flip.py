from qiskit import QuantumCircuit


def get_three_qubit_bit_flip_encoding_decoding_circuit():
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    return out
