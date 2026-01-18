from qiskit import QuantumCircuit

from .three_qubit_bit_flip import get_three_qubit_bit_flip_encoding_decoding_circuit, get_three_qubit_bit_flip_syndrome_extraction_circuit
from .three_qubit_phase_flip import get_three_qubit_phase_flip_decoding_circuit, get_three_qubit_phase_flip_encoding_circuit


def get_nine_qubit_shors_code_encoding_circuit() -> QuantumCircuit:
    """
    Encode
    - |0> as (|000> + |111>) ⊗ (|000> + |111>) ⊗ (|000> + |111>)
    - |1> as (|000> - |111>) ⊗ (|000> - |111>) ⊗ (|000> - |111>)
    """
    out = QuantumCircuit(9)
    out.compose(get_three_qubit_phase_flip_encoding_circuit(), qubits=(0, 3, 6), inplace=True)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(3, 4, 5), inplace=True)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(6, 7, 8), inplace=True)
    return out


def get_nine_qubit_shors_code_decoding_circuit() -> QuantumCircuit:
    out = QuantumCircuit(9)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(3, 4, 5), inplace=True)
    out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(6, 7, 8), inplace=True)
    out.compose(get_three_qubit_phase_flip_decoding_circuit(), qubits=(0, 3, 6), inplace=True)
    return out


def get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    out = QuantumCircuit(9 + 6)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 9, 10), inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(3, 4, 5, 11, 12), inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(6, 7, 8, 13, 14), inplace=True)
    return out
