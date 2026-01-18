from qiskit import QuantumCircuit

from qecc import get_three_qubit_phase_flip_encoding
from qecc.three_qubit_phase_flip import get_three_qubit_phase_flip_decoding

from .utils import CompBasisState, HadBasisState, QuantumCircuitTest


class TestThreeQubitBitFlipEncodingDecoding(QuantumCircuitTest):
    @staticmethod
    def encode(qc: QuantumCircuit) -> None:
        """
        Given a 3-qubit quantum circuit, apply the 3 qubit phase flip encoding circuit
        """
        qc.compose(get_three_qubit_phase_flip_encoding(), qubits=(0, 1, 2), inplace=True)

    @staticmethod
    def decode(qc: QuantumCircuit) -> None:
        """
        Given a 3-qubit quantum circuit, apply the 3 qubit phase flip decoding circuit
        """
        qc.compose(get_three_qubit_phase_flip_decoding(), qubits=(0, 1, 2), inplace=True)

    def test_encoding_0(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_two_results_50_50(qc, ("000", "111"))

    def test_encoding_1(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        # Same as for 0, because the phase on |111> vs -|111> isn't detectable by measurement
        self.check_results_two_results_50_50(qc, ("000", "111"))

    def test_encoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        # The phase-flip encoding circuit converts |+00> to |000>
        self.check_results_one_result(qc, "000")

    def test_encoding_decoding_0(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000")

    def test_encoding_decoding_1(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "001")

    def test_encoding_decoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        self.decode(qc)
        self.check_results_two_results_50_50(qc, ("000", "001"))
