from qiskit import QuantumCircuit, QuantumRegister

from .three_qubit_bit_flip import get_three_qubit_bit_flip_encoding_decoding_circuit, get_three_qubit_bit_flip_syndrome_extraction_circuit
from .three_qubit_phase_flip import get_three_qubit_phase_flip_decoding_circuit, get_three_qubit_phase_flip_encoding_circuit


def get_nine_qubit_shors_code_encoding_circuit() -> QuantumCircuit:
    """
    Encode
    - |0> as (|000> + |111>) ⊗ (|000> + |111>) ⊗ (|000> + |111>)
    - |1> as (|000> - |111>) ⊗ (|000> - |111>) ⊗ (|000> - |111>)
    """
    # One register for each bit flip block
    qregs = QuantumRegister(3), QuantumRegister(3), QuantumRegister(3)
    out = QuantumCircuit(*qregs)
    # Apply phase flip encoding on the first qubit of each bit-flip block
    out.compose(get_three_qubit_phase_flip_encoding_circuit(), qubits=[qreg[0] for qreg in qregs], inplace=True)
    # Apply bit flip encoding on each block
    for qreg in qregs:
        out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=qreg, inplace=True)
    return out


def get_nine_qubit_shors_code_decoding_circuit() -> QuantumCircuit:
    qregs = QuantumRegister(3), QuantumRegister(3), QuantumRegister(3)
    out = QuantumCircuit(*qregs)
    for qreg in qregs:
        out.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=qreg, inplace=True)
    out.compose(get_three_qubit_phase_flip_decoding_circuit(), qubits=[qreg[0] for qreg in qregs], inplace=True)
    return out


def get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    logical_qubit, bitflip_syndrome = QuantumRegister(9), QuantumRegister(6)
    out = QuantumCircuit(logical_qubit, bitflip_syndrome)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[:3] + bitflip_syndrome[:2], inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[3:6] + bitflip_syndrome[2:4], inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[6:9] + bitflip_syndrome[4:6], inplace=True)
    return out
