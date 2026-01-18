from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qecc import (
    get_three_qubit_bit_flip_encoding_decoding_circuit,
    get_three_qubit_bit_flip_syndrome_extraction_circuit,
)

from . import HadBasisState
from .utils import CompBasisState, QuantumCircuitTest


class TestThreeQubitBitFlipEncodingDecoding(QuantumCircuitTest):
    @staticmethod
    def get_initialized_qc(state_to_initialize: Statevector) -> QuantumCircuit:
        """
        Given a (normalized) state vector, return a 3-qubit quantum circuit with the first qubit initialised to the input vector
        """
        out = QuantumCircuit(3)
        out.initialize(state_to_initialize, [0])
        return out

    @staticmethod
    def encode_or_decode(qc: QuantumCircuit) -> None:
        """
        Given a 3-qubit quantum circuit, apply the 3 qubit bit flip encoding/decoding circuit
        """
        qc.compose(
            get_three_qubit_bit_flip_encoding_decoding_circuit(),
            qubits=(0, 1, 2),
            inplace=True,
        )

    @classmethod
    def check_results_one_result(cls, qc: QuantumCircuit, correct_result: str) -> None:
        """
        Given a quantum circuit and a single correct result, measure the circuit, and check the results of the measurement match the inputted correct result
        """
        qc.measure_all()
        # Reverse the order of correct results, because Qiskit works backwards
        correct_result_little_endian = correct_result[::-1]
        assert cls.simulate_circuit(qc) == {correct_result_little_endian: 1024}

    @classmethod
    def check_results_two_results_50_50(cls, qc: QuantumCircuit, correct_results: list[str]) -> None:
        """
        Given a quantum circuit and a list of 2 correct results, measure the circuit, and check the results of the measurement are approximately 50/50 between the two correct results (within +- 15%)
        """
        qc.measure_all()
        measurements = cls.simulate_circuit(qc)
        # Reverse the order of correct results, because Qiskit works backwards
        correct_results_little_endian = [res[::-1] for res in correct_results]
        # Test we have roughly 50/50 (+- 15%) of each correct result
        assert set(measurements.keys()) == set(correct_results_little_endian)
        assert 0.85 <= measurements[correct_results_little_endian[0]] / measurements[correct_results_little_endian[1]] <= 1.15

    def test_encoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "000")

    def test_encoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "111")

    def test_encoding_decoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode_or_decode(qc)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "100")

    def test_encoding_plus(self):
        qc = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode_or_decode(qc)
        self.check_results_two_results_50_50(qc, ["000", "111"])

    def test_encoding_decoding_plus(self):
        qc = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode_or_decode(qc)
        self.encode_or_decode(qc)
        self.check_results_two_results_50_50(qc, ["000", "100"])


class TestThreeQubitBitFlipSyndromeExtraction(QuantumCircuitTest):
    def test_encoding_0(self):
        qc = QuantumCircuit(5)
        qc.initialize(CompBasisState.ZERO, [0])
        # Encode
        qc.compose(
            get_three_qubit_bit_flip_encoding_decoding_circuit(),
            qubits=(0, 1, 2),
            inplace=True,
        )
        qc.barrier()
        # Syndrome extraction
        qc.compose(
            get_three_qubit_bit_flip_syndrome_extraction_circuit(),
            qubits=(0, 1, 2, 3, 4),
            inplace=True,
        )
        qc.barrier()
        # Measure
        qc.measure_all()

        assert self.simulate_circuit(qc) == {"00000": 1024}
