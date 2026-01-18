from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qecc import get_nine_qubit_shors_code_encoding_circuit
from qecc.nine_qubit_shors_code import apply_nine_qubit_shors_code_bit_flip_correction, get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit, get_nine_qubit_shors_code_decoding_circuit

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
            qubits=qc.qubits[:9],
            inplace=True,
        )

    @staticmethod
    def decode(qc: QuantumCircuit) -> None:
        """
        Given a 9-qubit quantum circuit, apply the 9 qubit Shor's code decoding circuit
        """
        qc.compose(
            get_nine_qubit_shors_code_decoding_circuit(),
            qubits=qc.qubits[:9],
            inplace=True,
        )

    @staticmethod
    def bit_flip_syndrome_extraction(qc: QuantumCircuit) -> None:
        qc.compose(
            get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit(),
            qubits=qc.qubits[:15],
            inplace=True,
        )

    @classmethod
    def get_bit_flip_error_correction_circuit(cls, state_to_initialize: Statevector, error_index: int | None) -> QuantumCircuit:
        # Initialise
        out = cls.get_initialized_qc(state_to_initialize, num_qubits=9 + 6, num_clbits=6)
        # Encode
        cls.encode(out)
        # Deliberate error
        if error_index is not None:
            out.x(error_index)
        # Syndrome extraction
        cls.bit_flip_syndrome_extraction(out)
        # Syndrome correction
        apply_nine_qubit_shors_code_bit_flip_correction(out)
        cls.decode(out)
        return out


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
        decoded_errored_strings = ("110", "010", "100")  # X on 1st, 2nd, 3rd qubit of block
        for i in range(9):
            qc = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=9 + 6)
            self.encode(qc)
            # Deliberate error
            qc.x(i)
            self.bit_flip_syndrome_extraction(qc)
            self.decode(qc)
            # Work out the correct measurement result:
            #  - The syndrome measurement is 01, 10, 11 depending i % 3, with 00's on either side depending on i // 3
            #  - The logical qubit measurement has similar 000 padding, and the block with the error's decoded value
            #    was worked out by hand
            syndrome_measurement = (2 - (i // 3)) * "00" + f"{(i % 3) + 1:02b}" + (i // 3) * "00"
            logical_qubit_measurement = (2 - (i // 3)) * "000" + decoded_errored_strings[i % 3] + (i // 3) * "000"
            self.check_results_one_result(qc, syndrome_measurement + logical_qubit_measurement)


class TestNineQubitShorsCodeBitFlipErrorCorrection(NineQubitShorsCodeTest):
    """
    Tests applying each possible X error, and making sure the correction works properly,
      on |0>, and |1> states
    """

    def test_correcting_0_deliberate_error(self):
        for error_index, syndrome in enumerate(["000001", "000010", "000011", "000100", "001000", "001100", "010000", "100000", "110000"]):
            qc = self.get_bit_flip_error_correction_circuit(CompBasisState.ZERO, error_index)
            self.check_results_one_result(qc, syndrome + "000000000", syndrome)

    def test_correcting_1_deliberate_error(self):
        for error_index, syndrome in enumerate(["000001", "000010", "000011", "000100", "001000", "001100", "010000", "100000", "110000"]):
            qc = self.get_bit_flip_error_correction_circuit(CompBasisState.ONE, error_index)
            self.check_results_one_result(qc, syndrome + "000000001", syndrome)
