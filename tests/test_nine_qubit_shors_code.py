from qiskit import QuantumCircuit

from qecc import get_nine_qubit_shors_code_encoding_circuit
from qecc.nine_qubit_shors_code import get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit, get_nine_qubit_shors_code_decoding_circuit

from . import HadBasisState
from .utils import CompBasisState, NineQubitEncodingQuantumCircuitTest, combs_of_strings


class NineQubitShorsCodeTest(NineQubitEncodingQuantumCircuitTest):
    ONE_SHOR_BLOCK_STRINGS = ("000", "111")
    ALL_VALID_SHORS_MEASUREMENTS = combs_of_strings(ONE_SHOR_BLOCK_STRINGS, ONE_SHOR_BLOCK_STRINGS, ONE_SHOR_BLOCK_STRINGS)

    @staticmethod
    def encode(qc: QuantumCircuit) -> None:
        """
        Given a 9-qubit quantum circuit, apply the 9 qubit Shor's code encoding circuit
        """
        qc.compose(
            get_nine_qubit_shors_code_encoding_circuit(),
            qubits=(0, 1, 2, 3, 4, 5, 6, 7, 8),
            inplace=True,
        )

    @staticmethod
    def decode(qc: QuantumCircuit) -> None:
        """
        Given a 9-qubit quantum circuit, apply the 9 qubit Shor's code decoding circuit
        """
        qc.compose(
            get_nine_qubit_shors_code_decoding_circuit(),
            qubits=(0, 1, 2, 3, 4, 5, 6, 7, 8),
            inplace=True,
        )

    @staticmethod
    def syndrome_extraction(qc: QuantumCircuit) -> None:
        qc.compose(
            get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit(),
            qubits=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
            inplace=True,
        )


class TestNineQubitShorsCodeEncodingDecoding(NineQubitShorsCodeTest):
    def test_encoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.ALL_VALID_SHORS_MEASUREMENTS)

    def test_encoding_decoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000000000")

    def test_encoding_decoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000000001")

    def test_encoding_decoding_plus(self):
        qc = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000000000", hadamard_qubits=1)

    def test_encoding_decoding_minus(self):
        qc = self.get_initialized_qc(HadBasisState.MINUS)
        self.encode(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000000001", hadamard_qubits=1)

    def test_encoding_decoding_random_state_vector(self):
        for _ in range(4):
            vec, zero_tally, one_tally = self.get_random_state_vector_and_measurement_results()

            qc = self.get_initialized_qc(vec)
            self.encode(qc)
            self.decode(qc)

            self.check_results_two_results_ratio(qc, ("000000000", "000000001"), ("", ""), (zero_tally, one_tally))


class TestNineQubitShorsCodeBitFlipSyndromeExtraction(NineQubitShorsCodeTest):
    def test_encoding_0_syndrome_deliberate_error(self):
        """
        Just testing 1 deliberate X-error, as I had to work out by hand what the effect of decoding the errored code
          without correction would be
        """
        qc = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=9 + 6)
        self.encode(qc)
        # Deliberate error
        qc.x(0)
        self.syndrome_extraction(qc)
        self.decode(qc)
        self.check_results_one_result(qc, "000001" + "000000110")
