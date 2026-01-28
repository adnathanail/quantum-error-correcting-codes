from qiskit import QuantumCircuit

from qecc.seven_qubit_steane_code import get_seven_qubit_steane_code_decoding_circuit, get_seven_qubit_steane_code_encoding_circuit

from .utils import CompBasisState, HadBasisState, SevenQubitEncodingQuantumCircuitTest


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
