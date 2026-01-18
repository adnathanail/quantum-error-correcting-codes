from pathlib import Path

from qecc.three_qubit_bit_flip import get_three_qubit_bit_flip_encoding_decoding_circuit

out_dir = Path(__file__).parent.parent / "imgs"

circuit = get_three_qubit_bit_flip_encoding_decoding_circuit()
circuit.draw("mpl", filename=str(out_dir / "three_qubit_bit_flip_encoding_decoding.png"))
