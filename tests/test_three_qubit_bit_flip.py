from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, random_statevector

from qecc import (
    apply_three_qubit_bit_flip_correction,
    get_three_qubit_bit_flip_encoding_decoding_circuit,
    get_three_qubit_bit_flip_syndrome_extraction_circuit,
)

from . import HadBasisState
from .utils import CompBasisState, ThreeQubitEncodingQuantumCircuitTest


class TestThreeQubitBitFlipEncodingDecoding(ThreeQubitEncodingQuantumCircuitTest):
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
        self.check_results_two_results_50_50(qc, ("000", "111"))

    def test_encoding_decoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode_or_decode(qc)
        self.encode_or_decode(qc)
        self.check_results_two_results_50_50(qc, ("000", "001"))


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
    """
    Tests applying each possible X error, and making sure the correction works properly,
      on |0>, |1>, and |+> states
    """

    @classmethod
    def get_error_correction_circuit(cls, state_to_initialize: Statevector, error_index: int | None) -> QuantumCircuit:
        # Initialise
        out, _, clreg = cls.get_initialized_qc(state_to_initialize, num_qubits=5, num_clbits=2)
        # Encode
        cls.encode_or_decode(out)
        # Deliberate error
        if error_index is not None:
            out.x(error_index)
        # Syndrome extraction
        cls.syndrome_extraction(out)
        # Syndrome correction
        apply_three_qubit_bit_flip_correction(out, clreg)
        return out

    def test_correcting_0_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ZERO, error_index)
            self.check_results_one_result(qc, syndrome + "000", syndrome)

    def test_correcting_1_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ONE, error_index)
            self.check_results_one_result(qc, syndrome + "111", syndrome)

    def test_correcting_plus_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(HadBasisState.PLUS, error_index)
            self.check_results_two_results_50_50(qc, (syndrome + "000", syndrome + "111"), (syndrome, syndrome))


class TestRandomThreeQubitBitFlipErrorCorrectionAndDecoding(TestThreeQubitBitFlipErrorCorrection):
    @classmethod
    def get_random_state_vector_and_measurement_results(cls) -> tuple[Statevector, int, int]:
        # Generate random 1-qubit state vector
        vec = random_statevector(2)
        # Measure the state vector, so we know roughly what the measurement results look like
        qc = QuantumCircuit(1)
        qc.initialize(vec)
        qc.measure_all()
        results = cls.simulate_circuit(qc)
        return vec, results["0"], results["1"]

    def test_random_state_vector_correction(self):
        """
        For a random state vector, apply each possible X error, and check the error is corrected, by checking
          the measurement results ratio of 0:1 is roughly the same as just the state vector by itself
        Repeated 4 times for safety
        """
        for _ in range(4):
            vec, zero_tally, one_tally = self.get_random_state_vector_and_measurement_results()
            for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
                qc = self.get_error_correction_circuit(vec, error_index)
                self.encode_or_decode(qc)

                self.check_results_two_results_ratio(qc, (syndrome + "000", syndrome + "001"), (syndrome, syndrome), (zero_tally, one_tally))
