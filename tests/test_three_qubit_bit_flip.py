from qiskit import QuantumCircuit

from src.three_qubit_bit_flip import get_three_qubit_bit_flip_encoding_decoding_circuit
from .utils import QuantumCircuitTest, CompBasisState


class TestThreeQubitBitFlipEncoding(QuantumCircuitTest):
    def test_encoding_0(self):
        qc = QuantumCircuit(3)
        qc.initialize(CompBasisState.ZERO, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Measure
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"000": 1024}

    def test_encoding_1(self):
        qc = QuantumCircuit(3)
        qc.initialize(CompBasisState.ONE, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Measure
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"111": 1024}

    def test_encoding_decoding_1(self):
        qc = QuantumCircuit(3)
        qc.initialize(CompBasisState.ONE, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Decode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Measure
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"001": 1024}
