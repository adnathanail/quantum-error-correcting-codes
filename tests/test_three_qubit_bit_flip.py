from qiskit import QuantumCircuit

from src.three_qubit_bit_flip import get_three_qubit_bit_flip_encoding_decoding_circuit
from .utils import QuantumCircuitTest, ZERO_STATE, ONE_STATE


class TestThreeQubitBitFlipEncoding(QuantumCircuitTest):
    def test_encoding_0(self):
        qc = QuantumCircuit(3)
        qc.initialize(ZERO_STATE, [0])
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"000": 1024}

    def test_encoding_1(self):
        qc = QuantumCircuit(3)
        qc.initialize(ONE_STATE, [0])
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"111": 1024}
