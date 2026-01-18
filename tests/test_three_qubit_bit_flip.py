from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from qecc import (
    apply_three_qubit_syndrome_correction,
    get_three_qubit_bit_flip_encoding_decoding_circuit,
    get_three_qubit_bit_flip_syndrome_extraction_circuit,
)

from . import HadBasisState
from .utils import CompBasisState, QuantumCircuitTest


class TestThreeQubitBitFlipEncodingDecoding(QuantumCircuitTest):
    @staticmethod
    def get_initialized_qc(state_to_initialize: Statevector, *, num_qubits: int = 3, num_clbits: int = 0) -> tuple[QuantumCircuit, QuantumRegister, ClassicalRegister]:
        """
        Given a (normalized) state vector, return a quantum circuit with the specified number of qubits, with the first qubit initialised to the input vector
        """
        qureg, clreg = QuantumRegister(num_qubits), ClassicalRegister(num_clbits)
        out = QuantumCircuit(qureg, clreg)
        out.initialize(state_to_initialize, [0])
        return out, qureg, clreg

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
    def check_results_one_result(cls, qc: QuantumCircuit, qreg_result: str, clreg_result: str = "") -> None:
        """
        Given a quantum circuit and a single correct result, measure the circuit, and check the results of the measurement match the inputted correct result
        """
        qc.measure_all()
        correct_result_little_endian = qreg_result + " " + clreg_result
        assert cls.simulate_circuit(qc) == {correct_result_little_endian: 1024}

    @classmethod
    def check_results_two_results_50_50(cls, qc: QuantumCircuit, correct_results: list[str]) -> None:
        """
        Given a quantum circuit and a list of 2 correct results, measure the circuit, and check the results of the measurement are approximately 50/50 between the two correct results (within +- 20%)
        """
        qc.measure_all()
        measurements = cls.simulate_circuit(qc)
        # Reverse the order of correct results, because Qiskit works backwards
        #   add a space, because adding an empty classical register adds a space to the output
        correct_results_little_endian = [res + " " for res in correct_results]
        # Test we have roughly 50/50 (+- 20%) of each correct result
        assert set(measurements.keys()) == set(correct_results_little_endian)
        assert 0.8 <= measurements[correct_results_little_endian[0]] / measurements[correct_results_little_endian[1]] <= 1.2

    def test_encoding_0(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "000")

    def test_encoding_1(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "111")

    def test_encoding_decoding_1(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode_or_decode(qc)
        self.encode_or_decode(qc)
        self.check_results_one_result(qc, "001")

    def test_encoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode_or_decode(qc)
        self.check_results_two_results_50_50(qc, ["000", "111"])

    def test_encoding_decoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode_or_decode(qc)
        self.encode_or_decode(qc)
        self.check_results_two_results_50_50(qc, ["000", "001"])


class TestThreeQubitBitFlipSyndromeExtraction(TestThreeQubitBitFlipEncodingDecoding):
    @staticmethod
    def syndrome_extraction(qc: QuantumCircuit) -> None:
        """
        Given a 5-qubit quantum circuit, apply the 3 qubit bit flip syndrome extraction circuit
        """
        qc.compose(
            get_three_qubit_bit_flip_syndrome_extraction_circuit(),
            qubits=(0, 1, 2, 3, 4),
            inplace=True,
        )

    def test_encoding_0_syndrome_no_error(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=5)
        self.encode_or_decode(qc)
        self.syndrome_extraction(qc)
        self.check_results_one_result(qc, "00000")

    def test_encoding_0_syndrome_deliberate_error(self):
        for error_index, measurement_outcome in [(0, "01001"), (1, "10010"), (2, "11100")]:
            qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=5)
            self.encode_or_decode(qc)
            # Deliberate error
            qc.x(error_index)
            self.syndrome_extraction(qc)
            self.check_results_one_result(qc, measurement_outcome)

    def test_encoding_1_syndrome_no_error(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE, num_qubits=5)
        self.encode_or_decode(qc)
        self.syndrome_extraction(qc)
        self.check_results_one_result(qc, "00111")

    def test_encoding_1_syndrome_deliberate_error(self):
        for error_index, measurement_outcome in [(0, "01110"), (1, "10101"), (2, "11011")]:
            qc, _, _ = self.get_initialized_qc(CompBasisState.ONE, num_qubits=5)
            self.encode_or_decode(qc)
            # Deliberate error
            qc.x(error_index)
            self.syndrome_extraction(qc)
            self.check_results_one_result(qc, measurement_outcome)


class TestThreeQubitBitFlipErrorCorrection(TestThreeQubitBitFlipSyndromeExtraction):
    def test_correcting_0_deliberate_error(self):
        qc, _, clreg = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=5, num_clbits=2)
        self.encode_or_decode(qc)
        # Deliberate error
        qc.x(0)
        self.syndrome_extraction(qc)
        apply_three_qubit_syndrome_correction(qc, clreg)
        self.check_results_one_result(qc, "01000", "01")
