# 000 — Environment pins

**Status:** accepted · **Phase:** P0.1 · **Date:** 2026-08-12

## Context

`CLAUDE.md` requires everything pinned in `pyproject.toml` with `uv.lock` committed.
Several pins were not free choices; this records the ones with a reason behind them.

## Decisions

### Python `>=3.11,<3.13`

`CLAUDE.md` requires 3.11+. The machine ships CPython 3.12.3, so 3.12 is the resolved
interpreter. Upper bound at 3.13 because `liboqs-python` 0.16.0 and the torch 2.6 CPU
wheels do not both cover 3.13 cleanly.

### Qiskit 1.4.2 + Aer 0.15.1 (staying on the 1.x line)

Qiskit 2.x exists, but P1 ports the owner's existing baseline
(`../multi_layer_security.py`), which was written against `qiskit>=1.0`. Invariant 8
forbids changing baseline behaviour, so the environment moves to the baseline, not the
other way round. Qiskit 1.4.2 is the final 1.x release.

Cost: aer 0.15.1's transpile path triggers several qiskit-1.3 `DeprecationWarning`s
from internals (`DAGCircuit.duration`, `Instruction.condition`). Our own code calls
none of them. `pyproject.toml` sets `filterwarnings = ["error", ...]` so any *new*
warning fails the suite, with a narrow exemption for messages matching
`deprecated as of qiskit`.

Revisit if P2/P3 need a Qiskit 2.x-only feature. Migration cost looks low — the
baseline touches only `QuantumCircuit`, `transpile`, and `AerSimulator`, all stable
across the 2.0 boundary.

### Torch 2.6.0 **CPU wheels**

> **Superseded rationale — see [`002-gpu-reevaluation.md`](002-gpu-reevaluation.md).**
> The driver was installed on 2026-08-12 and the choice was re-measured. **The pin is
> unchanged**, but it now rests on a benchmark (1.35× on the P1.3b shape, *0.55×* at
> batch 16) rather than on the absence of a driver. The paragraph below records the
> original reasoning as of the first P0.1 pass.

`nvidia-smi` fails on this machine: a GeForce 930MX (GM108M) is present but no driver
is loaded, and the active display adapter is Intel HD 620. CUDA wheels would add
~2.5 GB for no benefit, so `[tool.uv.sources]` points torch and torchvision at
`https://download.pytorch.org/whl/cpu`. `tests/test_environment.py` asserts the
`+cpu` local version tag so a silent lock drift to CUDA fails the suite.

**Consequence to plan for, not yet resolved:** P1.3b (train `DeepSteganography`) and
P4.3 (SRNet / Ye-Net / Zhu-Net on BOSSBase+BOWS2) are CPU-only on 4 cores. P4.3 in
particular is not realistically trainable here. Options are the fallback path already
in the plan (`create_simple_stego` for P1), fixing the NVIDIA driver, or renting a
GPU. Flagged to the owner at the end of P0.1; needs a decision before P4, not before
P1.

**Update (decision 002):** the driver has since been fixed and it was *not* enough —
the card is 2 GB and compute capability 5.0. P1.3b is fine on CPU either way; **P4.3
remains blocked** and now needs a rented GPU or a reduced-scale protocol.

### NumPy pinned to 1.26.4 (not 2.x)

Qiskit-Aer 0.15.1 wheels are built against the NumPy 1.x ABI. NumPy 2 is a separate,
avoidable variable in a codebase whose whole point is reproducible numbers.

### `pandas` + `pyarrow`

The experiment protocol in `CLAUDE.md` requires raw data as `.parquet` or `.npz`.
`pyarrow` is the parquet engine; without it the protocol is unimplementable.

## Reproducing the environment

```bash
./scripts/bootstrap_liboqs.sh   # native liboqs; see decision 001
uv sync --all-groups
uv run pytest
```
