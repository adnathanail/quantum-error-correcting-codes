from qiskit import QuantumCircuit


def get_three_qubit_phase_flip_encoding() -> QuantumCircuit:
    """
    Encode |0> as (|000> + |111>) and |1> as (|000> - |111>)
    """
    out = QuantumCircuit(3)
    out.h(0)
    out.cx(0, 1)
    out.cx(0, 2)
    return out


def get_three_qubit_phase_flip_decoding() -> QuantumCircuit:
    out = QuantumCircuit(3)
    out.cx(0, 1)
    out.cx(0, 2)
    out.h(0)
    return out
