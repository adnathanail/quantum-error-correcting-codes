import itertools
import math
from math import sqrt

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Statevector, random_statevector
from qiskit_aer import AerSimulator

simulator = AerSimulator()


class CompBasisState:
    ZERO = Statevector([1, 0])
    ONE = Statevector([0, 1])


class HadBasisState:
    PLUS = Statevector([1 / sqrt(2), 1 / sqrt(2)])
    MINUS = Statevector([1 / sqrt(2), -1 / sqrt(2)])


class QuantumCircuitTest:
    @staticmethod
    def get_initialized_qc(state_to_initialize: Statevector, *, num_qubits: int, clreg_sizes: tuple[int, ...] = (0,)) -> QuantumCircuit:
        """
        Given a (normalized) state vector, return a quantum circuit with the specified number of qubits, with the first
          qubit initialised to the input vector
        """
        clregs = [ClassicalRegister(size) for size in clreg_sizes]
        out = QuantumCircuit(QuantumRegister(num_qubits), *clregs)
        out.initialize(state_to_initialize, [0])
        return out

    @staticmethod
    def simulate_circuit(qc: QuantumCircuit) -> dict[str, int]:
        compiled_circuit = transpile(qc, simulator)
        result = simulator.run(compiled_circuit, shots=1024).result()
        return result.get_counts()

    @classmethod
    def _check_results_ratio(
        cls, qc: QuantumCircuit, qreg_results: tuple[str, ...], clreg_results: tuple[str, ...], expected_ratios: tuple[int, ...], *, num_std_devs: float = 4.0, hadamard_qubits: int = 0
    ) -> None:
        """
        Generic function to check quantum circuit measurement results against expected ratios.

        Uses binomial distribution to determine acceptable variance. With num_std_devs=4.0,
        a correct implementation has ~99.99% chance of passing.

        Args:
            qc: The quantum circuit to measure
            qreg_results: Tuple of expected quantum register measurement strings
            clreg_results: Tuple of expected classical register measurement strings
            expected_ratios: Tuple of ints representing the expected ratios (e.g., (1, 1) for 50/50, (1, 1, 1, 1) for even 4-way)
            num_std_devs: Number of standard deviations for tolerance (default 4.0)
        """
        for qb_index in range(hadamard_qubits):
            qc.h(qb_index)
        qc.measure_all()
        measurements = cls.simulate_circuit(qc)

        # Add a space, because adding an empty classical register adds a space to the output
        correct_results_little_endian = [qreg_results[i] + " " + clreg_results[i] for i in range(len(qreg_results))]

        # Check we only have the expected results
        assert set(measurements.keys()) == set(correct_results_little_endian), f"Measurements : {measurements}"

        total_shots = sum(measurements.values())
        ratio_sum = sum(expected_ratios)

        for i, result in enumerate(correct_results_little_endian):
            expected_prob = expected_ratios[i] / ratio_sum
            expected_count = total_shots * expected_prob
            std_dev = math.sqrt(total_shots * expected_prob * (1 - expected_prob))

            observed_count = measurements[result]
            tolerance = num_std_devs * std_dev

            assert abs(observed_count - expected_count) <= tolerance, f"Result '{result}': expected {expected_count:.0f} ± {tolerance:.0f}, got {observed_count}"

    @classmethod
    def check_results_one_result(cls, qc: QuantumCircuit, qreg_result: str, clreg_result: str = "", *, hadamard_qubits: int = 0) -> None:
        """
        Given a quantum circuit and a single correct result, measure the circuit, and check the results of the
          measurement match the inputted correct result
        """
        cls._check_results_ratio(qc, (qreg_result,), (clreg_result,), (1,), hadamard_qubits=hadamard_qubits)

    @classmethod
    def check_results_two_results_ratio(
        cls, qc: QuantumCircuit, qreg_results: tuple[str, str], clreg_results: tuple[str, str], expected_ratio: tuple[int, int], *, num_std_devs: float = 4.0, hadamard_qubits: int = 0
    ) -> None:
        """
        Given a quantum circuit and two expected results, measure the circuit and check the results
        match the expected ratio within statistical tolerance.
        """
        cls._check_results_ratio(qc, qreg_results, clreg_results, expected_ratio, num_std_devs=num_std_devs, hadamard_qubits=hadamard_qubits)

    @classmethod
    def check_results_n_results_even_chance(
        cls, qc: QuantumCircuit, qreg_results: tuple[str, ...], clreg_results: tuple[str, ...] | None = None, *, num_std_devs: float = 4.0, hadamard_qubits: int = 0
    ) -> None:
        """
        Given a quantum circuit and n expected results, measure the circuit and check the results
        are approximately evenly distributed among all outcomes.
        """
        if clreg_results is None:
            clreg_results = tuple("" for _ in qreg_results)
        expected_ratios = tuple(1 for _ in qreg_results)
        cls._check_results_ratio(qc, qreg_results, clreg_results, expected_ratios, num_std_devs=num_std_devs, hadamard_qubits=hadamard_qubits)

    @classmethod
    def check_results_two_results_50_50(cls, qc: QuantumCircuit, qreg_results: tuple[str, str], clreg_results: tuple[str, str] = ("", ""), hadamard_qubits: int = 0) -> None:
        """
        Given a quantum circuit and two expected results, measure the circuit and check the results
        are approximately 50/50 between the two.
        """
        cls.check_results_two_results_ratio(qc, qreg_results, clreg_results, expected_ratio=(1, 1), hadamard_qubits=hadamard_qubits)

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


class ThreeQubitEncodingQuantumCircuitTest(QuantumCircuitTest):
    ERROR_INDEXES_AND_SYNDROME_MEASUREMENTS: tuple[tuple[int | None, str], ...] = ((None, "00"), (0, "01"), (1, "10"), (2, "11"))

    @staticmethod
    def get_initialized_qc(state_to_initialize: Statevector, *, num_qubits: int = 3, clreg_sizes: tuple[int, ...] = (0,)) -> QuantumCircuit:
        return QuantumCircuitTest.get_initialized_qc(state_to_initialize, num_qubits=num_qubits, clreg_sizes=clreg_sizes)


class NineQubitEncodingQuantumCircuitTest(QuantumCircuitTest):
    @staticmethod
    def get_initialized_qc(state_to_initialize: Statevector, *, num_qubits: int = 9, clreg_sizes: tuple[int, ...] = (0,)) -> QuantumCircuit:
        return QuantumCircuitTest.get_initialized_qc(state_to_initialize, num_qubits=num_qubits, clreg_sizes=clreg_sizes)


def combs_of_strings(*strings: tuple[str, ...]):
    return ["".join(comb) for comb in itertools.product(*strings)]
