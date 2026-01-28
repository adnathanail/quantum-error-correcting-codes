"""
Reference https://stem.mitre.org/quantum/error-correction-codes/steane-ecc.html
"""

from qiskit import QuantumCircuit, QuantumRegister


def get_seven_qubit_steane_code_encoding_circuit() -> QuantumCircuit:
    """
    Encode
    - |0> as (|0000000> + |1010101> + |0110011> + |1100110> + |0001111> + |1011010> + |0111100> + |1101001>)
    - |1> as (|1111111> + |0101010> + |1001100> + |0011001> + |1110000> + |0100101> + |1000011> + |0010110>)
    """
    out = QuantumCircuit(7)
    # H
    out.h(4)
    out.h(5)
    out.h(6)
    # CNOT from 0
    out.cx(0, 1)
    out.cx(0, 2)
    # CNOT from 6
    out.cx(6, 3)
    out.cx(6, 1)
    out.cx(6, 0)
    # CNOT from 5
    out.cx(5, 3)
    out.cx(5, 2)
    out.cx(5, 0)
    # CNOT from 4
    out.cx(4, 3)
    out.cx(4, 2)
    out.cx(4, 1)
    return out


def get_seven_qubit_steane_code_decoding_circuit() -> QuantumCircuit:
    return get_seven_qubit_steane_code_encoding_circuit().inverse()


def get_seven_qubit_steane_code_syndrome_extraction_circuit() -> QuantumCircuit:
    logical_qubit, bit_flip_syndrome, phase_flip_syndrome = QuantumRegister(7), QuantumRegister(3), QuantumRegister(3)
    out = QuantumCircuit(logical_qubit, bit_flip_syndrome, phase_flip_syndrome)
    # Bit-flip
    for ctrl in (0, 2, 4, 6):
        out.cx(logical_qubit[ctrl], bit_flip_syndrome[0])
    for ctrl in (1, 2, 5, 6):
        out.cx(logical_qubit[ctrl], bit_flip_syndrome[1])
    for ctrl in (3, 4, 5, 6):
        out.cx(logical_qubit[ctrl], bit_flip_syndrome[2])
    # Phase-flip
    for i in range(3):
        out.h(phase_flip_syndrome[i])
    for targ in (0, 2, 4, 6):
        out.cx(phase_flip_syndrome[0], logical_qubit[targ])
    for targ in (1, 2, 5, 6):
        out.cx(phase_flip_syndrome[1], logical_qubit[targ])
    for targ in (3, 4, 5, 6):
        out.cx(phase_flip_syndrome[2], logical_qubit[targ])
    for i in range(3):
        out.h(phase_flip_syndrome[i])
    return out


def apply_seven_qubit_steane_code_correction(qc: QuantumCircuit) -> None:
    bit_flip_syndrome_measurement, phase_flip_syndrome_measurement = qc.cregs
    qc.measure(qc.qubits[7:10], bit_flip_syndrome_measurement)
    qc.measure(qc.qubits[10:13], phase_flip_syndrome_measurement)
    # Bit-flip correction
    with qc.if_test((bit_flip_syndrome_measurement, 0b001)):
        qc.x(0)
    with qc.if_test((bit_flip_syndrome_measurement, 0b010)):
        qc.x(1)
    with qc.if_test((bit_flip_syndrome_measurement, 0b011)):
        qc.x(2)
    with qc.if_test((bit_flip_syndrome_measurement, 0b100)):
        qc.x(3)
    with qc.if_test((bit_flip_syndrome_measurement, 0b101)):
        qc.x(4)
    with qc.if_test((bit_flip_syndrome_measurement, 0b110)):
        qc.x(5)
    with qc.if_test((bit_flip_syndrome_measurement, 0b111)):
        qc.x(6)
    # Phase-flip correction
    with qc.if_test((phase_flip_syndrome_measurement, 0b001)):
        qc.z(0)
    with qc.if_test((phase_flip_syndrome_measurement, 0b010)):
        qc.z(1)
    with qc.if_test((phase_flip_syndrome_measurement, 0b011)):
        qc.z(2)
    with qc.if_test((phase_flip_syndrome_measurement, 0b100)):
        qc.z(3)
    with qc.if_test((phase_flip_syndrome_measurement, 0b101)):
        qc.z(4)
    with qc.if_test((phase_flip_syndrome_measurement, 0b110)):
        qc.z(5)
    with qc.if_test((phase_flip_syndrome_measurement, 0b111)):
        qc.z(6)
