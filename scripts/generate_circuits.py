from pathlib import Path

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from qecc.three_qubit_bit_flip import apply_three_qubit_syndrome_correction, get_three_qubit_bit_flip_encoding_decoding_circuit, get_three_qubit_bit_flip_syndrome_extraction_circuit

out_dir = Path(__file__).parent.parent / "imgs"


def draw_circuit(circuit: QuantumCircuit, file_name: str) -> None:
    circuit.draw("mpl", filename=str(out_dir / file_name))


# === 3 qubit bit-flip ===
# Encoding
draw_circuit(get_three_qubit_bit_flip_encoding_decoding_circuit(), "three_qubit_bit_flip_encoding.png")

# Syndrome extraction
qc = QuantumCircuit(5)
qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
qc.barrier()
qc.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 3, 4), inplace=True)
draw_circuit(qc, "three_qubit_bit_flip_syndrome_extraction.png")

# Error correction
qureg, clreg = QuantumRegister(5), ClassicalRegister(2)
qc = QuantumCircuit(qureg, clreg)
qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
qc.barrier()
qc.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 3, 4), inplace=True)
qc.barrier()
apply_three_qubit_syndrome_correction(qc, clreg)
draw_circuit(qc, "three_qubit_bit_flip_error_correction.png")
