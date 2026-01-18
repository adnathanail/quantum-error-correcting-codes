from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qecc import get_three_qubit_phase_flip_encoding_circuit
from qecc.three_qubit_phase_flip import apply_three_qubit_phase_flip_correction, get_three_qubit_phase_flip_decoding_circuit, get_three_qubit_phase_flip_syndrome_extraction_circuit

from .utils import CompBasisState, HadBasisState, ThreeQubitEncodingQuantumCircuitTest


class ThreeQubitPhaseFlipTest(ThreeQubitEncodingQuantumCircuitTest):
    ALL_THREE_QUBIT_STATES: tuple[str, ...] = ("000", "001", "010", "011", "100", "101", "110", "111")

    @staticmethod
    def encode(qc: QuantumCircuit) -> None:
        """
        Given a 3-qubit quantum circuit, apply the 3 qubit phase flip encoding circuit
        """
        qc.compose(get_three_qubit_phase_flip_encoding_circuit(), qubits=(0, 1, 2), inplace=True)

    @staticmethod
    def decode(qc: QuantumCircuit) -> None:
        """
        Given a 3-qubit quantum circuit, apply the 3 qubit phase flip decoding circuit
        """
        qc.compose(get_three_qubit_phase_flip_decoding_circuit(), qubits=(0, 1, 2), inplace=True)

    @staticmethod
    def syndrome_extraction(qc: QuantumCircuit) -> None:
        """
        Given a 5-qubit quantum circuit, apply the 3 qubit phase flip syndrome extraction circuit
        """
        qc.compose(
            get_three_qubit_phase_flip_syndrome_extraction_circuit(),
            qubits=(0, 1, 2, 3, 4),
            inplace=True,
        )

    @classmethod
    def do_syndrome_testing(cls, initial_state: Statevector, error_index: int | None, measurement_results: tuple[str, ...], hadamard_basis: bool = False) -> None:
        qc, _, _ = cls.get_initialized_qc(initial_state, num_qubits=5)
        cls.encode(qc)
        # Deliberate error
        if error_index is not None:
            qc.z(error_index)
        cls.syndrome_extraction(qc)
        cls.check_results_n_results_even_chance(qc, measurement_results, hadamard_basis=hadamard_basis)

    @classmethod
    def get_error_correction_circuit(cls, state_to_initialize: Statevector, error_index: int | None) -> QuantumCircuit:
        # Initialise
        out, _, clreg = cls.get_initialized_qc(state_to_initialize, num_qubits=5, num_clbits=2)
        # Encode
        cls.encode(out)
        # Deliberate error
        if error_index is not None:
            out.z(error_index)
        # Syndrome extraction
        cls.syndrome_extraction(out)
        # Syndrome correction
        apply_three_qubit_phase_flip_correction(out, clreg)
        return out


class TestThreeQubitPhaseFlipEncodingDecoding(ThreeQubitPhaseFlipTest):
    def test_encoding_0(self):
        # Computational basis
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.ALL_THREE_QUBIT_STATES)
        # Hadamard basis
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_one_result(qc, "000", hadamard_basis=True)

    def test_encoding_1(self):
        # Computational basis
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        # Same as for 0, because the phase on |111> vs -|111> isn't detectable by measurement
        self.check_results_n_results_even_chance(qc, self.ALL_THREE_QUBIT_STATES)
        # Hadamard basis
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.check_results_one_result(qc, "111", hadamard_basis=True)

    def test_encoding_plus(self):
        # Computational basis
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        # The phase-flip encoding |+00> causes destructive interference, leaving only even parity states
        self.check_results_n_results_even_chance(qc, ("000", "011", "101", "110"))
        # Hadamard basis
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        self.check_results_two_results_50_50(qc, ("000", "111"), hadamard_basis=True)

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


class TestThreeQubitPhaseFlipSyndromeExtraction(ThreeQubitPhaseFlipTest):
    def test_encoding_0_and_1_syndrome_computational(self):
        """
        |0> and |1> encode to |+++> and |---> which aren't distinguishable when measuring in the computational basis
          and the phase introduced by the deliberate error, also isn't detectable, so the expected measurement outcome
          is a superposition over all 3 qubit states, plus the correct syndrome
        """
        for initial_state in [CompBasisState.ZERO, CompBasisState.ONE]:
            for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
                self.do_syndrome_testing(initial_state, error_index, tuple(syndrome + state for state in self.ALL_THREE_QUBIT_STATES))

    def test_encoding_0_syndrome_hadamard(self):
        for error_index, measurement_outcome in ((None, "00000"), (0, "01001"), (1, "10010"), (2, "11100")):
            self.do_syndrome_testing(CompBasisState.ZERO, error_index, (measurement_outcome,), hadamard_basis=True)

    def test_encoding_1_syndrome_hadamard(self):
        for error_index, measurement_outcome in ((None, "00111"), (0, "01110"), (1, "10101"), (2, "11011")):
            self.do_syndrome_testing(CompBasisState.ONE, error_index, (measurement_outcome,), hadamard_basis=True)


class TestThreeQubitPhaseFlipErrorCorrection(ThreeQubitPhaseFlipTest):
    """
    Tests applying each possible X error, and making sure the correction works properly,
      on |0>, |1>, and |+> states
    """

    def test_correcting_0_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ZERO, error_index)
            self.check_results_one_result(qc, syndrome + "000", syndrome, hadamard_basis=True)

    def test_correcting_1_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(CompBasisState.ONE, error_index)
            self.check_results_one_result(qc, syndrome + "111", syndrome, hadamard_basis=True)

    def test_correcting_plus_deliberate_error(self):
        for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
            qc = self.get_error_correction_circuit(HadBasisState.PLUS, error_index)
            self.check_results_two_results_50_50(qc, (syndrome + "000", syndrome + "111"), (syndrome, syndrome), hadamard_basis=True)
