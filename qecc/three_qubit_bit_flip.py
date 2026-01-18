from qiskit import ClassicalRegister, QuantumCircuit


def get_three_qubit_bit_flip_encoding_decoding_circuit() -> QuantumCircuit:
    """
    Encode |0> as |000> and |1> as |111>
    """
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    return out


def get_three_qubit_bit_flip_syndrome_extraction_circuit() -> QuantumCircuit:
    """
    Error in qubit 0 gives syndrome 01, qubit 1 10, qubit 2 11
    """
    out = QuantumCircuit(5)
    out.cx(0, 3)
    out.cx(1, 4)
    out.cx(2, 3)
    out.cx(2, 4)
    return out


def apply_three_qubit_syndrome_correction(qc: QuantumCircuit, clreg: ClassicalRegister) -> None:
    qc.measure((3, 4), clreg)
    with qc.if_test((clreg, 0b01)):
        qc.x(0)
    with qc.if_test((clreg, 0b10)):
        qc.x(1)
    with qc.if_test((clreg, 0b11)):
        qc.x(2)
