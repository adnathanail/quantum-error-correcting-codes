from qiskit import QuantumCircuit

from qecc.seven_qubit_steane_code import get_seven_qubit_steane_code_encoding_circuit

from .utils import CompBasisState, SevenQubitEncodingQuantumCircuitTest


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


class TestSevenQubitSteaneCodeEncodingDecoding(SevenQubitSteaneCodeTest):
    def test_encoding_0(self):
        qc = self.get_initialized_qc(CompBasisState.ZERO)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.STEANE_CODE_ZERO_STATES)

    def test_encoding_1(self):
        qc = self.get_initialized_qc(CompBasisState.ONE)
        self.encode(qc)
        self.check_results_n_results_even_chance(qc, self.STEANE_CODE_ONE_STATES)
