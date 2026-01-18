import random

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qecc import get_nine_qubit_shors_code_encoding_circuit
from qecc.nine_qubit_shors_code import (
    apply_nine_qubit_shors_code_bit_flip_correction,
    apply_nine_qubit_shors_code_phase_flip_correction,
    get_nine_qubit_shors_code_bit_flip_syndrome_extraction_circuit,
    get_nine_qubit_shors_code_decoding_circuit,
    get_nine_qubit_shors_code_phase_flip_syndrome_extraction_circuit,
    get_nine_qubit_shors_code_syndrome_extraction_circuit,
)

from . import HadBasisState
from .utils import CompBasisState, NineQubitEncodingQuantumCircuitTest, combs_of_strings


class NineQubitShorsCodeTest(NineQubitEncodingQuantumCircuitTest):
    ONE_SHOR_BLOCK_STRINGS = ("000", "111")
    ALL_VALID_SHORS_MEASUREMENTS = combs_of_strings(ONE_SHOR_BLOCK_STRINGS, ONE_SHOR_BLOCK_STRINGS, ONE_SHOR_BLOCK_STRINGS)
    BIT_FLIP_SYNDROMES = ("000001", "000010", "000011", "000100", "001000", "001100", "010000", "100000", "110000")
    PHASE_FLIP_SYNDROMES = ("01", "10", "11")

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
        out = cls.get_initialized_qc(state_to_initialize, num_qubits=9 + 6, clreg_sizes=(6,))
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

    @staticmethod
    def phase_flip_syndrome_extraction(qc: QuantumCircuit) -> None:
        qc.compose(
            get_nine_qubit_shors_code_phase_flip_syndrome_extraction_circuit(),
            qubits=qc.qubits,
            inplace=True,
        )

    @classmethod
    def get_phase_flip_error_correction_circuit(cls, state_to_initialize: Statevector, error_index: int | None) -> QuantumCircuit:
        # Initialise
        out = cls.get_initialized_qc(state_to_initialize, num_qubits=9 + 2, clreg_sizes=(2,))
        # Encode
        cls.encode(out)
        # Deliberate error
        if error_index is not None:
            out.z(error_index)
        # Syndrome extraction
        cls.phase_flip_syndrome_extraction(out)
        # Syndrome correction
        apply_nine_qubit_shors_code_phase_flip_correction(out)
        cls.decode(out)
        return out

    @staticmethod
    def complete_syndrome_extraction(qc: QuantumCircuit) -> None:
        qc.compose(
            get_nine_qubit_shors_code_syndrome_extraction_circuit(),
            qubits=qc.qubits,
            inplace=True,
        )

    @classmethod
    def get_complete_error_correction_circuit(cls, state_to_initialize: Statevector, bit_flip_error_index: int | None, phase_flip_error_index: int | None) -> QuantumCircuit:
        # Initialise
        out = cls.get_initialized_qc(state_to_initialize, num_qubits=9 + 6 + 2, clreg_sizes=(6, 2))
        # Encode
        cls.encode(out)
        # Deliberate error
        if bit_flip_error_index is not None:
            out.x(bit_flip_error_index)
        if phase_flip_error_index is not None:
            out.z(phase_flip_error_index)
        # Syndrome extraction
        cls.complete_syndrome_extraction(out)
        # Syndrome correction
        apply_nine_qubit_shors_code_bit_flip_correction(out)
        apply_nine_qubit_shors_code_phase_flip_correction(out)
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
            vec, prob_zero, prob_one = self.get_random_state_vector_and_exact_probabilities()

            qc = self.get_initialized_qc(vec)
            self.encode(qc)
            self.decode(qc)

            self.check_results_two_results_ratio(qc, ("000000000", "000000001"), ("", ""), (prob_zero, prob_one))


class TestNineQubitShorsCodeBitFlipSyndromeExtraction(NineQubitShorsCodeTest):
    def test_encoding_0_syndrome_deliberate_error(self):
        decoded_errored_strings = ("110", "010", "100")  # X on 1st, 2nd, 3rd qubit of block
        for error_index in range(9):
            qc = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=9 + 6)
            self.encode(qc)
            # Deliberate error
            qc.x(error_index)
            self.bit_flip_syndrome_extraction(qc)
            self.decode(qc)
            # Work out the correct measurement result:
            #  - The syndrome measurement is 01, 10, 11 depending i % 3, with 00's on either side depending on i // 3
            #  - The logical qubit measurement has similar 000 padding, and the block with the error's decoded value
            #    was worked out by hand
            logical_qubit_measurement = (2 - (error_index // 3)) * "000" + decoded_errored_strings[error_index % 3] + (error_index // 3) * "000"
            self.check_results_one_result(qc, self.BIT_FLIP_SYNDROMES[error_index] + logical_qubit_measurement)


class TestNineQubitShorsCodeBitFlipErrorCorrection(NineQubitShorsCodeTest):
    """
    Tests applying each possible X error, and making sure the correction works properly,
      on |0>, and |1> states
    """

    def test_correcting_0_deliberate_error(self):
        for error_index, syndrome in enumerate(self.BIT_FLIP_SYNDROMES):
            qc = self.get_bit_flip_error_correction_circuit(CompBasisState.ZERO, error_index)
            self.check_results_one_result(qc, syndrome + "000000000", syndrome)

    def test_correcting_1_deliberate_error(self):
        for error_index, syndrome in enumerate(self.BIT_FLIP_SYNDROMES):
            qc = self.get_bit_flip_error_correction_circuit(CompBasisState.ONE, error_index)
            self.check_results_one_result(qc, syndrome + "000000001", syndrome)


class TestNineQubitShorsCodePhaseFlipSyndromeExtraction(NineQubitShorsCodeTest):
    def test_encoding_0_syndrome_deliberate_error(self):
        logical_qubit_measurements_by_block = ("001001001", "000001000", "001000000")
        for error_index in range(9):
            qc = self.get_initialized_qc(CompBasisState.ZERO, num_qubits=9 + 2)
            self.encode(qc)
            # Deliberate error
            qc.z(error_index)
            self.phase_flip_syndrome_extraction(qc)
            self.decode(qc)
            # # Work out the correct measurement result:
            # #  - The syndrome measurement is 01 for Z in the first block, 10 2nd, 11 3rd
            # #  - The logical qubit measurement is always 001001001
            self.check_results_one_result(qc, self.PHASE_FLIP_SYNDROMES[error_index // 3] + logical_qubit_measurements_by_block[error_index // 3])


class TestNineQubitShorsCodePhaseFlipErrorCorrection(NineQubitShorsCodeTest):
    """
    Tests applying each possible Z error, and making sure the correction works properly,
      on |0>, and |1> states
    """

    def test_correcting_0_deliberate_error(self):
        for error_index_multiplier, syndrome in enumerate(self.PHASE_FLIP_SYNDROMES):
            for error_index_offset in range(3):
                qc = self.get_phase_flip_error_correction_circuit(CompBasisState.ZERO, error_index_multiplier * 3 + error_index_offset)
                self.check_results_one_result(qc, syndrome + "000000000", syndrome)

    def test_correcting_1_deliberate_error(self):
        for error_index_multiplier, syndrome in enumerate(self.PHASE_FLIP_SYNDROMES):
            for error_index_offset in range(3):
                qc = self.get_phase_flip_error_correction_circuit(CompBasisState.ONE, error_index_multiplier * 3 + error_index_offset)
                self.check_results_one_result(qc, syndrome + "000000001", syndrome)


class TestNineQubitShorsCodeCompleteErrorCorrection(NineQubitShorsCodeTest):
    """
    Tests applying each possible X and Z error, and making sure the correction works properly,
      on |0>, and |1> states
    """

    @classmethod
    def do_error_correction_testing(cls, initial_state: Statevector, measurement_outcome: str) -> None:
        for bit_flip_error_index, bit_flip_syndrome in enumerate(cls.BIT_FLIP_SYNDROMES):
            for phase_flip_error_index_multiplier, phase_flip_syndrome in enumerate(cls.PHASE_FLIP_SYNDROMES):
                for phase_flip_error_index_offset in range(3):
                    qc = cls.get_complete_error_correction_circuit(initial_state, bit_flip_error_index, phase_flip_error_index_multiplier * 3 + phase_flip_error_index_offset)
                    cls.check_results_one_result(qc, f"{phase_flip_syndrome}{bit_flip_syndrome}{measurement_outcome}", f"{phase_flip_syndrome} {bit_flip_syndrome}")

    def test_correcting_0_deliberate_error(self):
        self.do_error_correction_testing(CompBasisState.ZERO, "000000000")

    def test_correcting_1_deliberate_error(self):
        self.do_error_correction_testing(CompBasisState.ONE, "000000001")


class TestRandomNineQubitShorsCodeCompleteErrorCorrection(NineQubitShorsCodeTest):
    """
    Tests applying random X and Z errors to random state vectors, and making sure the correction works properly
    """

    def test_random_state_vector_correction(self):
        for _ in range(10):
            vec, prob_zero, prob_one = self.get_random_state_vector_and_exact_probabilities()
            bit_flip_error_index = random.randint(0, 8)
            phase_flip_error_index = random.randint(0, 8)

            bit_flip_syndrome = self.BIT_FLIP_SYNDROMES[bit_flip_error_index]
            phase_flip_syndrome = self.PHASE_FLIP_SYNDROMES[phase_flip_error_index // 3]

            qc = self.get_complete_error_correction_circuit(vec, bit_flip_error_index, phase_flip_error_index)

            self.check_results_two_results_ratio(
                qc,
                (f"{phase_flip_syndrome}{bit_flip_syndrome}000000000", f"{phase_flip_syndrome}{bit_flip_syndrome}000000001"),
                (f"{phase_flip_syndrome} {bit_flip_syndrome}", f"{phase_flip_syndrome} {bit_flip_syndrome}"),
                (prob_zero, prob_one),
                num_shots=100,
            )
