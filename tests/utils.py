from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

simulator = AerSimulator()


ZERO_STATE = Statevector([1, 0])
ONE_STATE = Statevector([0, 1])


class QuantumCircuitTest:
    @staticmethod
    def simulate_circuit(qc: QuantumCircuit) -> dict[str, int]:
        compiled_circuit = transpile(qc, simulator)
        result = simulator.run(compiled_circuit, shots=1024).result()
        return result.get_counts()
