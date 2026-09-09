"""
Thin Qiskit BackendV2 wrapper around the Fermioniq local dev server.

Copy this single file into your other project. It only depends on
`qiskit` -- no Fermioniq packages needed there -- and talks over HTTP to
`local_server/server.py`, which must be running in the Emulator repo
(`uv run python local_server/server.py`).

Example
-------
    from qiskit import QuantumCircuit
    from fermioniq_local_backend import FermioniqLocalBackend

    backend = FermioniqLocalBackend()  # defaults to http://127.0.0.1:8787

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    job = backend.run(qc, shots=1000)
    result = job.result()
    print(result.get_counts())
    print(result.results[0].metadata)  # runtime, bond dimension, fidelity, ...

    # Batch submission: pass a list of circuits and they run together as
    # one Fermioniq job (a single qcsim subprocess), not one job each.
    job = backend.run([qc1, qc2, qc3], shots=1000)
    result = job.result()
    print(result.get_counts(0), result.get_counts(1), result.get_counts(2))

    # Force a small bond dimension to deliberately induce approximation
    # (useful for studying accuracy/cost tradeoffs on a circuit that
    # would otherwise emulate exactly and give fidelity 1.0):
    job = backend.run(qc, shots=1000, bond_dimension=8)
    print(job.result().results[0].metadata["extrapolated_2qubit_gate_fidelity"])

    # Or let effort (0-1) pick the bond dimension the normal way:
    job = backend.run(qc, shots=1000, effort=0.05)
"""

import base64
import io
import json
import time
import urllib.error
import urllib.request
import uuid

from qiskit import qpy, transpile
from qiskit.circuit import Measure, Parameter, Reset
from qiskit.circuit.library import (
    CHGate,
    CRXGate,
    CRYGate,
    CRZGate,
    CUGate,
    CXGate,
    CZGate,
    HGate,
    IGate,
    PhaseGate,
    RGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXGate,
    TdgGate,
    TGate,
    UGate,
    XGate,
    YGate,
    ZGate,
)
from qiskit.providers import BackendV2, JobV1, Options
from qiskit.providers.jobstatus import JobStatus
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData
from qiskit.transpiler import Target

# Gates supported by Fermioniq's qiskit serializer -- note this is capped
# at 2-qubit gates (QCShared/src/qcshared/utils/constants.py:
# MAX_QUBITS_PER_GATE_OR_CHANNEL), so e.g. ccx/cswap/rccx are deliberately
# excluded here; run() transpiles into this basis so such gates still work,
# just decomposed.
# (QCShared/src/qcshared/utils/gate_maps.py:qiskit_gate_map)
_THETA = Parameter("theta")
_SUPPORTED_GATES = [
    XGate(),
    YGate(),
    ZGate(),
    HGate(),
    SGate(),
    SXGate(),
    SdgGate(),
    TGate(),
    TdgGate(),
    IGate(),
    RXGate(_THETA),
    RYGate(_THETA),
    RZGate(_THETA),
    RGate(_THETA, _THETA),
    UGate(_THETA, _THETA, _THETA),
    PhaseGate(_THETA),
    SwapGate(),
    CXGate(),
    CZGate(),
    CHGate(),
    CRZGate(_THETA),
    CRXGate(_THETA),
    CRYGate(_THETA),
    CUGate(_THETA, _THETA, _THETA, _THETA),
    RXXGate(_THETA),
    RYYGate(_THETA),
    RZZGate(_THETA),
    Measure(),
    Reset(),
]


def _http_json(url: str, method: str = "GET", payload: dict | None = None) -> tuple:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


class _Header(dict):
    """Minimal stand-in for qiskit's (deprecated, Qobj-era) experiment
    header. Different qiskit versions read this either via `.to_dict()`
    or by treating it as dict-like directly (e.g. `.items()`), so this
    supports both."""

    def __init__(self, **fields):
        super().__init__(fields)

    def to_dict(self):
        return dict(self)


class FermioniqJob(JobV1):
    """One Fermioniq server-side job, covering all circuits passed to
    backend.run() at once -- they run together as a single batch (one
    qcsim subprocess), not as separate submissions per circuit."""

    def __init__(self, backend, circuits, shots, effort=None, bond_dimension=None):
        super().__init__(backend, str(uuid.uuid4()))
        self._circuits = circuits
        self._shots = shots
        self._effort = effort
        self._bond_dimension = bond_dimension
        self._server_job_id = None

    def job_id(self) -> str:
        """Return the Fermioniq server-assigned job id once submitted.

        Falls back to the local placeholder id from ``__init__`` if called
        before ``submit()`` has run.
        """
        return self._server_job_id if self._server_job_id is not None else self._job_id

    def submit(self):
        if self._server_job_id is not None:
            raise RuntimeError("Job already submitted")

        circuits_b64 = []
        for circuit in self._circuits:
            buf = io.BytesIO()
            qpy.dump(circuit, buf)
            circuits_b64.append(base64.b64encode(buf.getvalue()).decode())

        payload = {
            "circuits": circuits_b64,
            "shots": self._shots,
            "effort": self._effort,
            "bond_dimension": self._bond_dimension,
        }
        status, body = _http_json(f"{self._backend.url}/jobs", method="POST", payload=payload)
        if status != 202:
            raise RuntimeError(f"Failed to submit batch: {body.get('error')}")
        self._server_job_id = body["job_id"]

    def status(self):
        _, body = _http_json(f"{self._backend.url}/jobs/{self._server_job_id}")
        return JobStatus.DONE if body["status"] == "finished" else JobStatus.RUNNING

    def result(self, timeout: float | None = None, wait: float = 0.2) -> Result:
        start = time.monotonic()
        while self.status() != JobStatus.DONE:
            if timeout is not None and time.monotonic() - start > timeout:
                raise TimeoutError("Timed out waiting for Fermioniq job to finish")
            time.sleep(wait)

        exp_results = []
        for i, circuit in enumerate(self._circuits):
            status, body = _http_json(f"{self._backend.url}/jobs/{self._server_job_id}/result/{i}")
            if status != 200:
                raise RuntimeError(f"Fermioniq job failed: {body.get('error')}")
            # Fermioniq samples the full qubit register regardless of where
            # measure() gates were placed, so the header describes all
            # qubits as one classical register rather than mirroring the
            # circuit's actual clbits/cregs.
            exp_results.append(
                ExperimentResult(
                    shots=body["shots"],
                    success=True,
                    data=ExperimentResultData(counts=body["counts"]),
                    header=_Header(
                        name=circuit.name,
                        memory_slots=circuit.num_qubits,
                        creg_sizes=[["meas", circuit.num_qubits]],
                    ),
                    # Fermioniq-specific diagnostics (runtime, bond
                    # dimension, estimated fidelity, gate counts) --
                    # accessible as result.results[i].metadata.
                    metadata=body["metadata"],
                )
            )

        return Result(
            backend_name=self._backend.name,
            backend_version=self._backend.backend_version,
            qobj_id="fermioniq-local",
            job_id=self.job_id(),
            success=True,
            results=exp_results,
        )


class FermioniqLocalBackend(BackendV2):
    """Qiskit backend that runs circuits on a Fermioniq local dev server."""

    def __init__(self, url: str = "http://127.0.0.1:8787", max_qubits: int = 32):
        super().__init__(name="fermioniq_local", backend_version="0.1.0")
        self.url = url.rstrip("/")

        target = Target(num_qubits=max_qubits)
        for gate in _SUPPORTED_GATES:
            target.add_instruction(gate, None)
        self._target = target

    @property
    def target(self) -> Target:
        return self._target

    @property
    def max_circuits(self):
        return None

    @classmethod
    def _default_options(cls) -> Options:
        return Options(shots=1000)

    def run(self, run_input, **options) -> FermioniqJob:
        """Run one or more circuits.

        In addition to `shots`, accepts two knobs that control the DMRG
        bond dimension (i.e. emulation accuracy/cost -- see
        fermioniq.config.defaults.standard_config):

        - `effort` (float, 0-1): picks the bond dimension the normal way.
          Higher effort = more accuracy, more memory/time.
        - `bond_dimension` (int): pins the bond dimension to an exact
          value directly, bypassing the automatic choice. Useful for
          deliberately forcing approximation on a circuit that would
          otherwise run exactly. Takes precedence over `effort` if both
          are given.

        Diagnostics for the actual run (including the bond dimension
        used, an estimated fidelity, and runtime) come back in
        `result.results[i].metadata`.
        """
        circuits = run_input if isinstance(run_input, list) else [run_input]
        # Decompose anything outside Fermioniq's supported gate set (e.g.
        # ccx, cswap -- see _SUPPORTED_GATES above) into gates it accepts.
        circuits = transpile(circuits, target=self.target)
        if not isinstance(circuits, list):
            circuits = [circuits]
        shots = options.get("shots", self.options.shots)
        effort = options.get("effort")
        bond_dimension = options.get("bond_dimension")
        job = FermioniqJob(self, circuits, shots, effort, bond_dimension)
        job.submit()
        return job
