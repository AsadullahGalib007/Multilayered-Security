# QSTEG-AE

Entropy-accounted hybrid quantum–classical covert channel. Research codebase; the
deliverable is a paper, not a product.

Incremental successor to Sykot et al., *Multi-Layered Security System: Integrating QKD
with Classical Cryptography to Enhance Steganographic Security* (arXiv:2408.06964v1).

- Project constitution: [`CLAUDE.md`](CLAUDE.md)
- Research proposal: [`docs/proposal.md`](docs/proposal.md)
- Phase plan and gates: [`docs/plan.md`](docs/plan.md)
- Decision records: [`docs/decisions/`](docs/decisions/)

## Setup

Requires [`uv`](https://docs.astral.sh/uv/), Python 3.11–3.12, and a C toolchain
(`git`, `cmake`, `make`, `gcc`) for the native PQC library.

```bash
./scripts/bootstrap_liboqs.sh   # build native liboqs — REQUIRED, and not in uv.lock
uv sync --all-groups            # create .venv from uv.lock
uv run pytest                   # test suite
uv run ruff check . && uv run black --check .
```

Environment sanity check (must pass before any phase work):

```bash
uv run python -c "import qiskit_aer, oqs, torch; print('ok')"
```

**The bootstrap step is not optional.** `liboqs-python` (imported as `oqs`) ships no
native library; it tries to cmake-build one on first import, and that build needs
OpenSSL headers this machine does not have. The script builds liboqs with
`-DOQS_USE_OPENSSL=OFF` instead. It is idempotent, so re-running it is free. Full
story in [`docs/decisions/001-pqc-library.md`](docs/decisions/001-pqc-library.md).

Torch is pinned to **CPU wheels**. The machine has a GeForce 930MX with a working
driver, but it was benchmarked and does not earn the swap — 1.35× on the P1.3b
workload and *slower* than CPU at batch 16, with only 2 GB of VRAM. Measurements and
the consequences for P4.3 are in
[`docs/decisions/002-gpu-reevaluation.md`](docs/decisions/002-gpu-reevaluation.md).
[`docs/decisions/000-environment-pins.md`](docs/decisions/000-environment-pins.md)
records the remaining pins, including why the project stays on the Qiskit 1.x line.

## Running experiments

One script per experiment ID, re-runnable with a single command:

```bash
uv run python -m experiments.<experiment_id> --seed 20240816 --out results/<experiment_id>
```

Every run writes `results/<id>/manifest.json` (git SHA, seed, params, package
versions, wall time, hostname) plus raw data as `.parquet`/`.npz`. `results/` is
gitignored except for manifests.

## Layout

```
src/baseline/       faithful port of arXiv:2408.06964 — FROZEN, do not fix
src/qkd/            E91 circuits, sifting, CHSH, noise models
src/postproc/       M1: parameter estimation, reconciliation, verification, Toeplitz PA
src/keymgmt/        M2/M5: hybrid combiner, HKDF ratchet, budget scheduler
src/aead/           M3: AES-256-GCM, AAD binding, nonce discipline
src/stego/          M4: encrypt-then-embed, HILL/S-UNIWARD/STC, learned nets
src/steganalysis/   SRM, Ye-Net, Zhu-Net, SRNet detectors
src/metrics/        NPCR, UACI, entropy, PSNR/SSIM/LPIPS, P_E
src/viz/            figure generation, single shared style
experiments/        one script per experiment ID
results/            generated (gitignored except manifests)
data/               BOSSBase, BOWS2, ALASKA2 (gitignored; see data/README.md)
```

## Non-negotiables

No number without a seed. No claim without an artifact. Crypto primitives come from
vetted libraries only. `src/baseline/` reproduces the base paper *including its
flaws* — those flaws are the paper's evidence. Full list in `CLAUDE.md`.
