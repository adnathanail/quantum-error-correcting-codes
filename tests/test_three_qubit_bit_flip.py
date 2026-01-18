import math

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector, random_statevector

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
        Given a (normalized) state vector, return a quantum circuit with the specified number of qubits, with the first
          qubit initialised to the input vector
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
        Given a quantum circuit and a single correct result, measure the circuit, and check the results of the
          measurement match the inputted correct result
        """
        qc.measure_all()
        correct_result_little_endian = qreg_result + " " + clreg_result
        assert cls.simulate_circuit(qc) == {correct_result_little_endian: 1024}

    @classmethod
    def check_results_two_results_ratio(
        cls,
        qc: QuantumCircuit,
        qreg_results: tuple[str, str],
        clreg_results: tuple[str, str],
        expected_ratio: tuple[int, int],
        num_std_devs: float = 4.0,
    ) -> None:
        """
        Given a quantum circuit and two expected results, measure the circuit and check the results
        match the expected ratio within statistical tolerance.

        Uses binomial distribution to determine acceptable variance. With num_std_devs=4.0,
        a correct implementation has ~99.99% chance of passing.

        Args:
            qc: The quantum circuit to measure
            qreg_results: Tuple of two expected quantum register measurement strings
            clreg_results: Tuple of two expected classical register measurement strings
            expected_ratio: Tuple of two ints representing the expected ratio (e.g., (1, 1) for 50/50, (3, 1) for 75/25)
            num_std_devs: Number of standard deviations for tolerance (default 4.0)
        """
        qc.measure_all()
        measurements = cls.simulate_circuit(qc)

        # Add a space, because adding an empty classical register adds a space to the output
        correct_results_little_endian = [qreg_results[i] + " " + clreg_results[i] for i in range(2)]

        # Check we only have the expected results
        assert set(measurements.keys()) == set(correct_results_little_endian)

        total_shots = sum(measurements.values())
        ratio_sum = expected_ratio[0] + expected_ratio[1]

        for i, result in enumerate(correct_results_little_endian):
            expected_prob = expected_ratio[i] / ratio_sum
            expected_count = total_shots * expected_prob
            std_dev = math.sqrt(total_shots * expected_prob * (1 - expected_prob))

            observed_count = measurements[result]
            tolerance = num_std_devs * std_dev

            assert abs(observed_count - expected_count) <= tolerance, f"Result '{result}': expected {expected_count:.0f} ± {tolerance:.0f}, got {observed_count}"

    @classmethod
    def check_results_two_results_50_50(cls, qc: QuantumCircuit, qreg_results: tuple[str, str], clreg_results: tuple[str, str] = ("", "")) -> None:
        """
        Given a quantum circuit and two expected results, measure the circuit and check the results
        are approximately 50/50 between the two.
        """
        cls.check_results_two_results_ratio(qc, qreg_results, clreg_results, expected_ratio=(1, 1))

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

    ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS: tuple[tuple[int | None, str], ...] = ((None, "00"), (0, "01"), (1, "10"), (2, "11"))

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
        apply_three_qubit_syndrome_correction(out, clreg)
        return out

    def test_correcting_0_deliberate_error(self):
        for error_index, syndrome_measurement_outcome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ZERO, error_index)
            self.check_results_one_result(qc, syndrome_measurement_outcome + "000", syndrome_measurement_outcome)

    def test_correcting_1_deliberate_error(self):
        for error_index, syndrome_measurement_outcome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ONE, error_index)
            self.check_results_one_result(qc, syndrome_measurement_outcome + "111", syndrome_measurement_outcome)

    def test_correcting_plus_deliberate_error(self):
        for error_index, syndrome_measurement_outcome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(HadBasisState.PLUS, error_index)
            self.check_results_two_results_50_50(qc, (syndrome_measurement_outcome + "000", syndrome_measurement_outcome + "111"), (syndrome_measurement_outcome, syndrome_measurement_outcome))


class TestRandomThreeQubitBitFlipErrorCorrection(TestThreeQubitBitFlipErrorCorrection):
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
            for error_index, syndrome_measurement_outcome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
                qc = self.get_error_correction_circuit(vec, error_index)
                self.encode_or_decode(qc)

                self.check_results_two_results_ratio(
                    qc, (syndrome_measurement_outcome + "000", syndrome_measurement_outcome + "001"), (syndrome_measurement_outcome, syndrome_measurement_outcome), (zero_tally, one_tally)
                )
