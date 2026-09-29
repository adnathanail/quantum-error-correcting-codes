import json

import fermioniq
import rich
from fermioniq.client import Client
from qiskit import QuantumCircuit

with open("token-alex.json") as f:
    access_tokens = json.load(f)

print(access_tokens)
client = Client(access_token_id=access_tokens["access_token_id"], access_token_secret=access_tokens["access_token_secret"])


def qiskit_bell_pair():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit


circuit = qiskit_bell_pair()

emulator_job = fermioniq.EmulatorJob(circuit=circuit)
result = client.schedule_and_wait(emulator_job)

rich.print(result)
rich.print(result.job_metadata)
