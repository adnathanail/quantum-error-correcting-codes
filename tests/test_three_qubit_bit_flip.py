from qiskit import QuantumCircuit

from qecc import get_three_qubit_bit_flip_encoding_decoding_circuit, get_three_qubit_bit_flip_syndrome_extraction_circuit

from . import HadBasisState
from .utils import CompBasisState, QuantumCircuitTest


class TestThreeQubitBitFlipEncodingDecoding(QuantumCircuitTest):
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

    def test_encoding_plus(self):
        qc = QuantumCircuit(3)
        qc.initialize(HadBasisState.PLUS, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Measure
        qc.measure_all()

        measurements = self.simulate_circuit(qc)
        # Test we have roughly 50/50 (+- 10%) 000 and 111 state
        assert set(measurements.keys()) == {"000", "111"}
        assert 0.9 <= measurements["000"] / measurements["111"] <= 1.1

    def test_encoding_decoding_plus(self):
        qc = QuantumCircuit(3)
        qc.initialize(HadBasisState.PLUS, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Decode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        # Measure
        qc.measure_all()

        measurements = self.simulate_circuit(qc)
        # Test we have roughly 50/50 (+- 10%) 000 and 001 state
        assert set(measurements.keys()) == {"000", "001"}
        assert 0.9 <= measurements["000"] / measurements["001"] <= 1.1


class TestThreeQubitBitFlipSyndromeExtraction(QuantumCircuitTest):
    def test_encoding_0(self):
        qc = QuantumCircuit(5)
        qc.initialize(CompBasisState.ZERO, [0])
        # Encode
        qc.compose(get_three_qubit_bit_flip_encoding_decoding_circuit(), qubits=(0, 1, 2), inplace=True)
        qc.barrier()
        # Syndrome extraction
        qc.compose(get_three_qubit_bit_flip_syndrome_extraction_circuit(), qubits=(0, 1, 2, 3, 4), inplace=True)
        qc.barrier()
        # Measure
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"00000": 1024}
