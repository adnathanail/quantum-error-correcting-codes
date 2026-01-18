from qiskit import QuantumCircuit

from qecc import get_three_qubit_phase_flip_encoding_circuit
from qecc.three_qubit_phase_flip import get_three_qubit_phase_flip_decoding_circuit, get_three_qubit_phase_flip_syndrome_extraction_circuit

from .utils import CompBasisState, HadBasisState, ThreeQubitEncodingQuantumCircuitTest


class TestThreeQubitPhaseFlipEncodingDecoding(ThreeQubitEncodingQuantumCircuitTest):
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

    def test_encoding_0(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.ALL_THREE_QUBIT_STATES)

    def test_encoding_1(self):
        qc, _, _ = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        # Same as for 0, because the phase on |111> vs -|111> isn't detectable by measurement
        self.check_results_n_results_even_chance(qc, self.ALL_THREE_QUBIT_STATES)

    def test_encoding_plus(self):
        qc, _, _ = self.get_initialized_qc(HadBasisState.PLUS)
        self.encode(qc)
        # The phase-flip encoding |+00> causes destructive interference, leaving only even parity states
        self.check_results_n_results_even_chance(qc, ("000", "011", "101", "110"))

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


class TestThreeQubitPhaseFlipSyndromeExtraction(TestThreeQubitPhaseFlipEncodingDecoding):
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

    def test_encoding_0_and_1_syndrome(self):
        """
        |0> and |1> encode to |+++> and |---> which aren't distinguishable when measuring in the computational basis
          and the phase introduced by the deliberate error, also isn't detectable, so the expected measurement outcome
          is a superposition over all 3 qubit states, plus the correct syndrome
        """
        for initial_state in [CompBasisState.ZERO, CompBasisState.ONE]:
            for error_index, syndrome in self.ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS:
                qc, _, _ = self.get_initialized_qc(initial_state, num_qubits=5)
                self.encode(qc)
                # Deliberate error
                if error_index is not None:
                    qc.z(error_index)
                self.syndrome_extraction(qc)
                self.check_results_n_results_even_chance(qc, tuple(syndrome + state for state in self.ALL_THREE_QUBIT_STATES))
