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
    logical_qubit, bit_flip_syndrome = QuantumRegister(9), QuantumRegister(6)
    out = QuantumCircuit(logical_qubit, bit_flip_syndrome)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[:3] + bit_flip_syndrome[:2], inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[3:6] + bit_flip_syndrome[2:4], inplace=True)
    out.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[6:9] + bit_flip_syndrome[4:6], inplace=True)
    return out


def apply_nine_qubit_shors_code_bit_flip_correction(qc: QuantumCircuit) -> None:
    clreg = qc.cregs[0]
    qc.measure(qc.qubits[9 : 9 + 6], clreg)
    for index, syndrome in enumerate([0b000001, 0b000010, 0b000011, 0b000100, 0b001000, 0b001100, 0b010000, 0b100000, 0b110000]):
        with qc.if_test((clreg, syndrome)):
            qc.x(index)


def get_nine_qubit_shors_code_phase_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    logical_qubit, phase_flip_syndrome = QuantumRegister(9), QuantumRegister(2)
    out = QuantumCircuit(logical_qubit, phase_flip_syndrome)
    out.h(phase_flip_syndrome[0])
    out.h(phase_flip_syndrome[1])
    # Syndrome 01 (block 1)
    for i in range(3):
        out.cx(phase_flip_syndrome[0], logical_qubit[i])
    # Syndrome 10 (block 2)
    for i in range(3, 6):
        out.cx(phase_flip_syndrome[1], logical_qubit[i])
    # Syndrome 11 (block 3)
    for i in range(6, 9):
        out.cx(phase_flip_syndrome[0], logical_qubit[i])
        out.cx(phase_flip_syndrome[1], logical_qubit[i])
    out.h(phase_flip_syndrome[0])
    out.h(phase_flip_syndrome[1])
    return out


def apply_nine_qubit_shors_code_phase_flip_correction(qc: QuantumCircuit) -> None:
    clreg = qc.cregs[-1]
    qc.measure(qc.qubits[-2:], clreg)
    with qc.if_test((clreg, 0b01)):
        qc.z(0)
    with qc.if_test((clreg, 0b10)):
        qc.z(3)
    with qc.if_test((clreg, 0b11)):
        qc.z(6)


def get_nine_qubit_shors_code_syndrome_extraction_circuit() -> QuantumCircuit:
    logical_qubit, bit_flip_syndrome, phase_flip_syndrome = QuantumRegister(9), QuantumRegister(6), QuantumRegister(2)
    out = QuantumCircuit(logical_qubit, bit_flip_syndrome, phase_flip_syndrome)
    out.compose(get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit(), qubits=logical_qubit[:] + bit_flip_syndrome[:], inplace=True)
    out.compose(get_nine_qubit_shors_code_phase_flip_syndrome_extraction_circuit(), qubits=logical_qubit[:] + phase_flip_syndrome[:], inplace=True)
    return out
