from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qecc.seven_qubit_steane_code import get_seven_qubit_steane_code_decoding_circuit, get_seven_qubit_steane_code_encoding_circuit, get_seven_qubit_steane_code_syndrome_extraction_circuit

from .utils import CompBasisState, HadBasisState, SevenQubitEncodingQuantumCircuitTest, flip_bit_at_index


class SevenQubitSteaneCodeTest(SevenQubitEncodingQuantumCircuitTest):
    STEANE_CODE_ZERO_STATES = tuple(code[::-1] for code in ("0000000", "1010101", "0110011", "1100110", "0001111", "1011010", "0111100", "1101001"))
    STEANE_CODE_ONE_STATES = tuple(code[::-1] for code in ("1111111", "0101010", "1001100", "0011001", "1110000", "0100101", "1000011", "0010110"))

    @staticmethod
    def encode(qc: QuantumCircuit) -> None:
        """
        Given a 7-qubit quantum circuit, apply the 7 qubit Steane code encoding circuit
        """
        qc.compose(
            get_seven_qubit_steane_code_encoding_circuit(),
            qubits=qc.qubits[:7],
            inplace=True,
        )

    @staticmethod
    def decode(qc: QuantumCircuit) -> None:
        """
        Given a 7-qubit quantum circuit, apply the 7 qubit Steane code encoding circuit
        """
        qc.compose(
            get_seven_qubit_steane_code_decoding_circuit(),
            qubits=qc.qubits[:7],
            inplace=True,
        )

    @staticmethod
    def syndrome_extraction(qc: QuantumCircuit) -> None:
        qc.compose(
            get_seven_qubit_steane_code_syndrome_extraction_circuit(),
            qubits=qc.qubits[:13],
            inplace=True,
        )


class TestSevenQubitSteaneCodeEncodingDecoding(SevenQubitSteaneCodeTest):
    def test_encoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.STEANE_CODE_ZERO_STATES)

    def test_encoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.STEANE_CODE_ONE_STATES)

    def test_encoding_decoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "0000000")

    def test_encoding_decoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "0000001")

    def test_encoding_decoding_plus(self):
        qc = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "0000000", hadamard_qubits=1)

    def test_encoding_decoding_minus(self):
        qc = self.get_initialized_qc(HadBasisState.MINUS)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "0000001", hadamard_qubits=1)

    def test_encoding_decoding_random_state_vector(self):
        for _ in range(4):
            vec, prob_zero, prob_one = self.get_random_state_vector_and_exact_probabilities()

            qc = self.get_initialized_qc(vec)
            self.encode(qc)
            self.decode(qc)

            self.check_results_two_results_ratio(qc, ("0000000", "0000001"), ("", ""), (prob_zero, prob_one))


class TestSevenQubitSteaneCodeSyndromeExtraction(SevenQubitSteaneCodeTest):
    DECODED_ERROR_STRINGS = ("001", "010", "011", "100", "101", "110", "111")

    @classmethod
    def do_syndrome_x_error_test(cls, initial_state: Statevector, un_errored_states: tuple[str, ...]) -> None:
        for error_index in range(7):
            qc = cls.get_initialized_qc(initial_state, num_qubits=7 + 3 + 3)
            cls.encode(qc)
            # Deliberate error
            qc.x(error_index)
            cls.syndrome_extraction(qc)
            # Correct measurements: for each un-errored state encoding
            # - Phase flip syndrome: 000
            # - Bit flip syndrome: error index in binary
            # - Logical qubit: state encoding with the correct bit flipped
            correct_measurements = tuple("000" + cls.DECODED_ERROR_STRINGS[error_index] + flip_bit_at_index(state, error_index) for state in un_errored_states)
            cls.check_results_n_results_even_chance(qc, correct_measurements)

    def test_encoding_0_syndrome_deliberate_x_error(self):
        self.do_syndrome_x_error_test(CompBasisState.ZERO, self.STEANE_CODE_ZERO_STATES)

    def test_encoding_1_syndrome_deliberate_x_error(self):
        self.do_syndrome_x_error_test(CompBasisState.ONE, self.STEANE_CODE_ONE_STATES)

    @classmethod
    def do_syndrome_z_error_test(cls, initial_state: Statevector, un_errored_states: tuple[str, ...]) -> None:
        for error_index in range(7):
            qc = cls.get_initialized_qc(initial_state, num_qubits=7 + 3 + 3)
            cls.encode(qc)
            # Deliberate error
            qc.z(error_index)
            cls.syndrome_extraction(qc)
            # Correct measurements: for each un-errored state encoding
            # - Phase flip syndrome: error index in binary
            # - Bit flip syndrome: 000
            # - Logical qubit: state encoding (phase flips won't affect computational basis measurement)
            correct_measurements = tuple(cls.DECODED_ERROR_STRINGS[error_index] + "000" + state for state in un_errored_states)
            cls.check_results_n_results_even_chance(qc, correct_measurements)

    def test_encoding_0_syndrome_deliberate_z_error(self):
        self.do_syndrome_z_error_test(CompBasisState.ZERO, self.STEANE_CODE_ZERO_STATES)

    def test_encoding_1_syndrome_deliberate_z_error(self):
        self.do_syndrome_z_error_test(CompBasisState.ONE, self.STEANE_CODE_ONE_STATES)
