# CLAUDE.md — QSTEG-AE

Project constitution. Read fully before any task. Do not skip sections.

## What this is

Research codebase for **QSTEG-AE**: an entropy-accounted hybrid quantum-classical covert channel. It is the incremental successor to Sykot et al., *Multi-Layered Security System: Integrating QKD with Classical Cryptography to Enhance Steganographic Security* (arXiv:2408.06964v1). PDF lives at `../core paper/2408.06964v1.pdf`.

Output is a **paper**, not a product. Every line of code exists to produce a number, figure, or table that goes in the paper. Code that produces nothing publishable is scope creep — say so and stop.

Full research proposal: `docs/proposal.md`. Execution plan and gates: `docs/plan.md`. Read both before starting a phase.

## Prior art in the parent repo — read this first

`../` already contains a **working implementation of the base paper**, written by the owner:

| File | Contains |
|---|---|
| `../multi_layer_security.py` | `E91QKD`, `CryptographicSystem` (SHA-256 → AES-**CBC**, line 242), `ImageAnalysis`, `MultiLayeredSecuritySystem` |
| `../deep_steganography.py` | `PrepNetwork`, `HidingNetwork`, `RevealNetwork`, `DeepSteganography` |
| `../complete_demo.py`, `../quick_test.py` | End-to-end drivers |
| `../requirements.txt`, `../environment.yml` | qiskit, qiskit-aer, pycryptodome, torch |

`multi_layer_security.py:308` — `calculate_npcr_uaci(original_image, encrypted_image)` — is the plain-vs-cipher bug, implemented exactly as the paper describes it. **This is evidence, not a defect to fix.**

**Port this code into `src/baseline/`. Do not rewrite it from scratch, and do not correct it.** Corrected metrics live in `src/metrics/` as separate functions alongside the frozen originals.

## Owner

Asadullah (@abrgalib). He reviews at every phase gate. He is the sole author of scientific claims — you generate evidence, he decides what it means.

## Hard invariants

Violating any of these invalidates the paper. Treat a violation as a build failure.

1. **No number without a seed.** Every experiment sets an explicit RNG seed and records it in the result artifact. Unseeded randomness in a results path is a bug.
2. **No claim without an artifact.** Any number that appears in a table or figure must be regenerable by one command, from a committed script, into `results/<experiment_id>/`. If it only lives in a notebook, it does not exist.
3. **Cryptographic primitives come from vetted libraries.** `cryptography` / `pycryptodome` for AES-GCM, `liboqs-python` or `pqcrypto` for ML-KEM, `hashlib`/`hmac` for HKDF. **Never hand-roll AES, SHA, HKDF, or ML-KEM.** Hand-rolled crypto in a security paper is an automatic reject.
4. **Nonce reuse is a critical bug.** AES-GCM nonces come from a monotonic counter in the ratchet, never from `random`. Add an assertion that trips on reuse; keep it in the test suite.
5. **Never claim information-theoretic security for anything downstream of the PQC combiner.** The hybrid key is computationally secure. Say so in code comments and in the paper.
6. **ε-parameters are always explicit.** Any function returning a secret key returns its `(ε_cor, ε_sec)` alongside. No bare `bytes` returns from the post-processing chain.
7. **Simulator ≠ hardware.** Every claim about key rates carries the qualifier that it is Qiskit Aer, not photons. Do not let this slip out of the abstract.
8. **Baseline reproduction is sacred.** `src/baseline/` reimplements the base paper *as written*, including its flaws. Never "fix" the baseline. Its flaws are the paper's evidence.

## Stack

- Python 3.11+, `uv` for env management
- Qiskit + Qiskit Aer (quantum sim, noise models)
- `cryptography` (AES-256-GCM, HKDF), `pycryptodome` fallback
- `liboqs-python` for ML-KEM-768 (FIPS 203); `pqcrypto` as fallback
- PyTorch for hiding/revealing nets and steganalysis (SRNet, Ye-Net, Zhu-Net)
- NumPy / SciPy / scikit-image for metrics; `piq` or `lpips` for LPIPS
- Matplotlib for figures. One style file, `src/viz/style.py`, used everywhere.
- pytest for tests; `ruff` + `black` for lint/format

Pin everything in `pyproject.toml`. Record `uv.lock`.

## Repo layout

```
qsteg-ae/
├── CLAUDE.md               ← this file
├── docs/
│   ├── proposal.md         ← research proposal (source of truth for the science)
│   ├── plan.md             ← phase plan + gate checklists
│   ├── decisions/          ← ADRs, one file per non-obvious choice
│   └── paper/              ← LaTeX, built last
├── src/
│   ├── baseline/           ← faithful reimplementation of arXiv:2408.06964 (DO NOT FIX)
│   ├── qkd/                ← E91 circuits, sifting, CHSH, noise models
│   ├── postproc/           ← M1: param est, Cascade/LDPC, error verification, Toeplitz PA
│   ├── keymgmt/            ← M2/M5: hybrid combiner, HKDF ratchet, budget scheduler
│   ├── aead/               ← M3: AES-GCM wrapper, AAD binding, nonce discipline
│   ├── stego/              ← M4: encrypt-then-embed, HILL/S-UNIWARD/STC, learned nets
│   ├── steganalysis/       ← SRM, Ye-Net, Zhu-Net, SRNet detectors
│   ├── metrics/            ← NPCR, UACI, entropy, PSNR/SSIM/LPIPS, P_E
│   └── viz/                ← figure generation, single style
├── experiments/            ← one script per experiment ID (e1_qber_sweep.py, ...)
├── results/                ← generated, gitignored except manifests
├── tests/
└── data/                   ← BOSSBase, BOWS2, ALASKA2 (gitignored, documented in README)
```

## Experiment protocol

Every experiment script:

1. Declares `EXPERIMENT_ID` and a one-line purpose docstring
2. Takes `--seed` (default fixed), `--out results/<id>/`
3. Writes `manifest.json`: git commit SHA, seed, all params, package versions, wall time, hostname
4. Writes raw data as `.parquet` or `.npz` — never only a plot
5. Writes figures via `src/viz`, never inline matplotlib config
6. Is re-runnable: `python -m experiments.<id>` and nothing else

If an experiment takes >10 min, add `--smoke` for a fast reduced-scale version and use it in CI.

## Reporting discipline

When you finish a task, report:

- what ran, what the numbers are
- what **contradicts** the proposal's expectation (this is the most valuable thing you can say)
- what you could not verify
- next task

Do **not** report "everything works." Report what the evidence shows. If a result favors the base paper over QSTEG-AE, say so immediately and loudly — that changes the paper's framing and the owner needs it same-day, not at the gate.

## Forbidden

- Fabricating or extrapolating a number to fill a table. If an experiment did not run, the cell is `TODO`, never a plausible value.
- Citing a paper you have not verified exists. Every citation gets a DOI or arXiv ID checked against the source.
- Tuning an experiment until QSTEG-AE wins. Report the honest curve; if the honest curve is unflattering, that is the finding.
- Committing datasets, model checkpoints >50MB, or `results/` payloads.
- Advancing past a phase gate without the owner's explicit sign-off.
- Touching `../core paper/` — it is read-only reference material.

## Git

- Branch per phase: `phase/p1-baseline`, `phase/p2-postproc`, …
- Conventional commits. One logical change per commit.
- Never commit to `main` directly; `main` only receives merges at phase gates.
- Tag each gate: `gate-p1`, `gate-p2`, …

## When stuck

Two failed attempts at the same thing → stop, write what you tried in `docs/decisions/`, and ask. Do not spiral. A blocked task reported in 20 minutes is cheap; four hours of thrashing is not.
