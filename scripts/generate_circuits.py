from pathlib import Path

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from qecc.three_qubit_bit_flip import apply_three_qubit_syndrome_correction, get_three_qubit_bit_flip_encoding_decoding_circuit, get_three_qubit_bit_flip_syndrome_extraction_circuit

imgs_dir = Path(__file__).parent.parent / "imgs"


def draw_circuit(circuit: QuantumCircuit, file_path: Path) -> None:
    circuit.draw("mpl", filename=str(file_path))


def three_qubit_bit_flip() -> None:
    out_dir = imgs_dir / "three_qubit_bit_flip"
    # Encoding
    draw_circuit(get_three_qubit_bit_flip_encoding_decoding_circuit(), out_dir / "encoding_decoding.png")

    # Syndrome extraction
    qc = QuantumCircuit(5)
    qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
    qc.barrier()
    qc.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 3, 4), inplace=True)
    draw_circuit(qc, out_dir / "syndrome_extraction.png")

    # Error correction
    qureg, clreg = QuantumRegister(5), ClassicalRegister(2)
    qc = QuantumCircuit(qureg, clreg)
    qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
    qc.barrier()
    qc.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 3, 4), inplace=True)
    qc.barrier()
    apply_three_qubit_syndrome_correction(qc, clreg)
    draw_circuit(qc, out_dir / "error_correction.png")


if __name__ == "__main__":
    three_qubit_bit_flip()
