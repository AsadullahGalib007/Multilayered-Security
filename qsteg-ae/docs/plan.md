# QSTEG-AE — Phase-Gated Execution Plan

For Claude Code. Owner (Asadullah) reviews at every gate. **Do not cross a gate without explicit sign-off.**

Science source of truth: `docs/proposal.md`. Rules: `CLAUDE.md`.

**Total: ~14 weeks. 6 phases. 6 gates.**

Legend — each task has: **Do** (what to build) · **Done when** (acceptance criteria, objective) · **Risk** (what goes wrong).

---

## P0 — Setup (2 days, no gate)

**P0.1 — Environment**
- Do: `uv` project, pin Qiskit/Aer, `cryptography`, `liboqs-python`, PyTorch, NumPy, SciPy, scikit-image, pytest, ruff, black. Commit `uv.lock`.
- Done when: `uv run pytest` passes on an empty suite; `uv run python -c "import qiskit_aer, oqs, torch"` succeeds.
- Risk: `liboqs-python` needs a native build. If it fails on this machine, fall back to `pqcrypto` and record the swap in `docs/decisions/001-pqc-library.md`.

**P0.2 — Skeleton + CI**
- Do: create the layout in `CLAUDE.md`. Add `src/viz/style.py`, `experiments/_template.py` implementing the manifest protocol, and a GitHub Actions (or local pre-commit) run of ruff + black + pytest + `--smoke` experiments.
- Done when: `python -m experiments._template` writes a valid `results/_template/manifest.json` with git SHA and seed.

**P0.3 — Datasets**
- Do: fetch BOSSBase 1.01, BOWS2, ALASKA2. Document exact source + checksum in `data/README.md`. Gitignore the payloads.
- Done when: checksums verified; a loader in `src/stego/data.py` yields 512×512 grayscale tensors.
- Risk: ALASKA2 is large (~30GB). Start with BOSSBase; ALASKA2 can wait until P4.

---

## P1 — Port, audit, and falsify (weeks 1–2) — **the hook**

> **A working baseline already exists** in the parent repo (`../multi_layer_security.py`, `../deep_steganography.py`, `../complete_demo.py`, `../quick_test.py`). It implements `E91QKD`, `CryptographicSystem` (SHA-256 → **AES-CBC**, confirmed at `multi_layer_security.py:242`), `ImageAnalysis`, `DeepSteganography` (Prep/Hiding/Reveal nets), and — critically — `calculate_npcr_uaci(original_image, encrypted_image)` at `multi_layer_security.py:308`, which is the wrong-metric bug computed exactly as diagnosed.
>
> **Do not rewrite it. Port it.** P1 is an audit, not a build.

**P1.1 — Port and freeze the baseline**
- Do: copy the existing modules into `src/baseline/` unchanged in behaviour. Add type hints, seeds, and a manifest-emitting entry point — nothing else. Record provenance (source file, git SHA of the parent repo) in `docs/decisions/001-baseline-provenance.md`.
- Done when: `python -m experiments.p1_baseline_smoke` reproduces `quick_test.py`'s output within noise; every module imports cleanly under the new env; `src/baseline/` is tagged and frozen per `CLAUDE.md` invariant 8.
- Note: AES mode ambiguity is **resolved** — the existing implementation chose CBC with a random IV. Record it, and note in the paper that the base paper itself never specifies the mode, which is the actual defect.

**P1.2 — Audit the baseline against the paper**
- Do: line-by-line check that the port matches arXiv:2408.06964's described method. Log every place the implementation had to guess (basis sign convention, CHSH subset selection, sifting rule, padding, IV handling).
- Done when: `docs/decisions/002-baseline-deviations.md` lists every guess with the paper's page/equation it fills in. This becomes the paper's "the method as published is underspecified" argument — a real contribution on its own.
- Risk: if a guess materially changes results (e.g. sifting rule alters key length), test both branches and report the sensitivity.

**P1.3 — Verify the E91 layer**
- Do: confirm CHSH and key statistics on the ported `E91QKD`. Noiseless first.
- Done when: |CHSH| ≥ 2.7 noiseless; sifted-key fraction ≈ 2/9 of singlets; key lengths for 25/100/250/500 singlets within ±20 % of the paper's 7/25/57/106 bits.
- Note: those four rate numbers are already published twice (base paper + the 2025 COMPAS Qiskit-E91 paper, identical values). Reproduce them to establish the port is faithful, then **never present them as a contribution**.

**P1.3b — Steganography layer check**
- Do: train/evaluate the existing `DeepSteganography` (Prep/Hiding/Reveal) as-is. `create_simple_stego` exists as a fallback path.
- Done when: revealed-secret PSNR ≥ 30 dB, stego-vs-cover PSNR ≥ 35 dB. If the existing nets underperform, use `create_simple_stego` for P1 and defer quality work to P4 — stego quality is not what P1 proves.
- Time-box: 3 days. Escalate rather than overrun.

**P1.4 — Reproduce their tables**
- Do: recompute entropy, NPCR, UACI, key rate, enc/dec time **using the paper's apparent definitions**.
- Done when: entropy reproduces 7.98–7.9995; NPCR reproduces ~99.5–99.8 %; **UACI reproduces 54–57 % when computed plain-vs-cipher**. That reproduction is the proof of the error.

**P1.5 — The falsification (E3 preview)**
- Do: the ported `ImageAnalysis.calculate_npcr_uaci(original, encrypted)` is the bug — keep it frozen as `npcr_uaci_as_published()`. Add a **new** `npcr_uaci_differential()` in `src/metrics/` that computes it *correctly* — cipher(P) vs cipher(P′), P′ = P with one pixel LSB flipped. Compare both against theoretical ideals:
  ```
  E[NPCR] = (1 − 2⁻⁸)·100 = 99.6094 %
  E[UACI] = Σ_{i=1..255} i(i+1) / (255·256²) · 100 = 33.4635 %
  ```
  Include Wu et al.'s hypothesis-test critical values, not just point estimates.
- Done when: a table with four columns — paper's value, our plain-vs-cipher reproduction, our correct differential value, theoretical ideal — for all four image sizes. Correct UACI must land near 33.46 %.

**P1.6 — The collapse (E1 preview)**
- Do: the existing `E91QKD.run_protocol()` is noiseless. Add a depolarizing `NoiseModel` to the Aer backend **without touching the frozen baseline logic** — inject it at the backend level. Sweep noise so QBER runs 0 → 12 %. At each point, measure whether Alice's and Bob's SHA digests match, and whether AES-CBC decryption recovers the image.
- Done when: a curve showing baseline decryption success ≈ 100 % at QBER = 0 and ≈ 0 % at any QBER above ~0.5 %. Report the exact QBER at which success drops below 50 %.
- Risk: **if the baseline somehow survives noise, the paper's lead changes.** Report this within the hour, not at the gate.

### 🚦 GATE P1 — owner review
Present:
- [ ] Port fidelity: does `src/baseline/` reproduce `quick_test.py` / `complete_demo.py`?
- [ ] Deviations log — how many places was the published method underspecified?
- [ ] Reproduction table (their numbers vs ours) — do we match?
- [ ] Corrected NPCR/UACI table with theoretical ideals and critical values
- [ ] QBER collapse curve + the 50 %-failure threshold
- [ ] Anything that contradicted the proposal
**Decision:** confirm the hook holds, or re-frame before spending P2.

---

## P2 — Composable post-processing (weeks 3–5) — **the rigor**

Goal: replace the bare hash with a real, ε-accounted QKD post-processing chain. Module M1.

**P2.1 — Parameter estimation**
- Do: QBER estimation from a disclosed random subset; CHSH S estimation; finite-sample confidence bounds (Hoeffding or Serfling for sampling without replacement).
- Done when: on a known-QBER simulated channel, the estimator's confidence interval covers truth ≥ 95 % of the time over 1000 trials.

**P2.2 — Information reconciliation**
- Do: Cascade first (simpler, correct, well-documented). Then rate-adaptive LDPC as the efficiency arm. Track leakage `ℓ_EC` in bits, measured not assumed.
- Done when: post-reconciliation key mismatch = 0 for QBER ≤ 11 %; reconciliation efficiency `f = ℓ_EC / (n·h(Q))` reported, with Cascade landing in the 1.05–1.20 range.
- Risk: LDPC is the time sink. **Cascade alone unblocks P3.** If LDPC slips, ship Cascade and defer LDPC to a P5 efficiency section.

**P2.3 — Error verification**
- Do: 2-universal hash tag exchange; abort on mismatch. Compute `ε_cor`.
- Done when: injected residual errors are caught with probability ≥ 1 − 2⁻ᵗ for tag length t; test with deliberate single-bit corruption.

**P2.4 — Privacy amplification**
- Do: Toeplitz-matrix PA (FFT-based for speed). Output length from the finite-key bound:
  ```
  ℓ ≤ n[1 − h(Q_x)] − ℓ_EC − log₂(2/ε_cor) − 2log₂(1/(2ε_PA))
  ```
- Done when: output length matches an independent hand computation to the bit for three worked parameter sets; PA throughput measured in Mbps and reported.

**P2.5 — Chain integration**
- Do: single `postproc.derive_key(raw, params) -> (key, ε_cor, ε_sec, diagnostics)`. Enforce invariant 6 (no bare `bytes` return).
- Done when: end-to-end run at QBER = 4.5 % (the realistic BBM92 reference) yields a nonzero ε-secure key and a matching key on both sides.

**P2.6 — Experiments E1 + E2**
- E1: full QBER sweep, baseline vs QSTEG-AE, decryption success + key agreement + final key length. **This is the paper's headline figure.**
- E2: ℓ_secure vs block size n ∈ [10³, 10⁷] at ε = 10⁻¹⁰, for Q ∈ {1, 3, 5, 8} %. Mark where the base paper's 106-bit key falls.
- Done when: both figures generated through `src/viz`, with manifests, and E2 shows a nonzero-key threshold block size.

### 🚦 GATE P2 — owner review
- [ ] E1 headline figure — is the contrast as strong as predicted?
- [ ] E2 finite-key scaling — does the 106-bit key fall below the security threshold as expected?
- [ ] ε-budget table (ε_cor, ε_sec, ε_PA and their composition)
- [ ] Reconciliation efficiency `f` — competitive or embarrassing?
- [ ] Is the LDPC arm in, or deferred?
**Decision:** this is the go/no-go for Q1 ambition. If the finite-key work is rigorous here, aim TIFS. If it is shaky, settle for Q2 and stop gold-plating.

---

## P3 — Key management + AEAD (weeks 6–7) — **the engineering**

Modules M2, M3, M5. Lower scientific risk, high reviewer-satisfaction return.

**P3.1 — Hybrid combiner (M2)**
- Do: `K = HKDF(K_QKD ‖ K_MLKEM ‖ K_ECDH, salt, info)`. ML-KEM-768 via liboqs. Concatenation order fixed and documented.
- Done when: known-answer tests pass for ML-KEM; combiner output changes if *any* input changes; a written argument (in `docs/decisions/`) that security holds if any one component survives.
- Risk: do not invent a combiner. Follow the construction in the cited hybrid literature and cite it.

**P3.2 — AEAD layer (M3)**
- Do: AES-256-GCM. AAD = `(cover_id, embed_params, payload_len, seq_no)`, canonically serialized. XChaCha20-Poly1305 as comparator.
- Done when: tag verification rejects every tampered ciphertext and every AAD mismatch across 10⁴ random mutations; **nonce-reuse assertion fires** in a deliberate-misuse test.

**P3.3 — Ratchet + budget scheduler (M5)**
- Do: HKDF chain seeded per QKD block; per-image key derivation; re-seed policy on bit budget or elapsed time. Define and implement:
  ```
  KCE = QKD secure bits consumed / secret payload bits delivered
  ```
- Done when: a simulated 24-hour session at 12 bps delivers a stated number of images without key starvation; KCE reported; forward secrecy verified (a compromised chain state does not recover earlier keys).

**P3.4 — Experiments E6 + E8**
- E6: throughput/latency/memory for QSTEG-AE vs baseline vs PQC-only vs ECDH-only. Include Toeplitz PA cost — the line everyone omits.
- E8: attack suite — known-plaintext, chosen-plaintext, ciphertext tampering, nonce-reuse, intercept-resend on the quantum link (show S drops below 2).

### 🚦 GATE P3 — owner review
- [ ] Combiner construction + its security argument
- [ ] E6 performance table — what does the rigor cost in ms?
- [ ] E8 attack results — anything unexpectedly broken?
- [ ] KCE numbers and the 24-hour session simulation
**Decision:** freeze the crypto stack. No more changes below the stego layer after this gate.

---

## P4 — Encrypt-then-embed + steganalysis (weeks 8–11) — **the risk**

Module M4. Longest, most uncertain phase. Budget accordingly.

**P4.1 — Inversion**
- Do: restructure to `secret → AEAD → ciphertext → embed into cover → stego on the wire in clear`.
- Done when: end-to-end round trip recovers the secret bit-exactly; the transmitted artifact is a normal-looking image, and its histogram/entropy resembles a natural photo — **not** the uniform noise the baseline transmits. Include a side-by-side figure; it is rhetorically powerful.

**P4.2 — Adaptive-cost embedding**
- Do: HILL and S-UNIWARD cost functions with STC (syndrome-trellis codes) as the classical arm. An INN or GAN hiding net as the learned arm.
- Done when: at 0.2 bpp, stego PSNR ≥ 40 dB and SSIM ≥ 0.98; payload extraction BER = 0 on a clean channel.
- Risk: STC implementations are fiddly. A correct simulated-embedding-efficiency stand-in is acceptable if documented — but say so plainly in the paper.

**P4.3 — Steganalysis suite**
- Do: SRM + ensemble classifier, Ye-Net, Zhu-Net, SRNet. Train on BOSSBase + BOWS2, test on ALASKA2 for the generalization claim.
- Done when: detectors reproduce published accuracy on WOW/S-UNIWARD at 0.4 bpp within a few points. **If they do not reproduce, the detectors are broken and every P_E number is worthless** — fix before proceeding.

**P4.4 — Experiments E4 + E5**
- E4: `P_E` (min average detection error) vs payload 0.05–0.5 bpp, for baseline encrypted-stego, QSTEG-AE encrypt-then-embed, and clean covers.
- E5: PSNR / SSIM / LPIPS; robustness under JPEG QF ∈ {50, 75, 95}, Gaussian σ ∈ {1, 3, 5}, resize ±25 %, crop 5 %. Report payload BER post-attack.
- Done when: both curve sets generated with manifests; the baseline's encrypted-stego should be trivially detectable (P_E → 0) while QSTEG-AE holds a meaningful P_E.
- Risk: **the honest result may be that QSTEG-AE is also detectable at high payload.** That is fine and publishable — report the operating point where it stops being detectable. Do not tune to win.

### 🚦 GATE P4 — owner review
- [ ] Side-by-side: what the baseline puts on the wire vs what we do
- [ ] E4 detectability curves — where is the safe operating point?
- [ ] E5 robustness table
- [ ] Did the detectors reproduce published numbers? (If no, nothing here counts.)
**Decision:** the stego chapter's story. If detectability is bad, pivot the framing toward the crypto contributions and present stego as a bounded-capacity result.

---

## P5 — Ablation + corrections (weeks 12–13)

**P5.1 — E7 ablation**
- Do: drop M1…M5 one at a time; report security and performance deltas.
- Done when: a five-row table where each row names exactly what breaks without that module.

**P5.2 — E3 final**
- Do: finalize the corrected-metrics section with hypothesis tests and critical values, not just point estimates.
- Done when: table + prose ready to drop into the paper.

**P5.3 — Reproducibility pass**
- Do: wipe `results/`, re-run every experiment from clean checkout, diff against committed manifests.
- Done when: every number regenerates within stated tolerance. Any that does not is a bug fixed before the gate.

**P5.4 — Citation audit**
- Do: verify every reference resolves to a real DOI/arXiv ID with matching title and authors.
- Done when: zero unverified citations. (The owner has personally caught fabricated references in peer review — this repo will not be the source of any.)

### 🚦 GATE P5 — owner review
- [ ] Ablation table
- [ ] Clean-room reproduction succeeded
- [ ] Citation audit clean
**Decision:** results are frozen. Writing starts.

---

## P6 — Paper (weeks 14–16)

**P6.1** — LaTeX skeleton in target venue template. Sections per proposal §6.
**P6.2** — Draft §3 (analysis of the existing pipeline) first — it is the hook and it is already fully evidenced from P1.
**P6.3** — Figures: regenerate all at publication DPI through `src/viz`. Consistent style, colorblind-safe, legible at print size.
**P6.4** — Draft remaining sections. Limitations section states plainly: Qiskit Aer simulation, not photonic hardware.
**P6.5** — Self-review against the venue's reviewer guidelines. Then owner review. Then submit.

### 🚦 GATE P6 — owner sign-off before submission

---

## Standing rules for Claude Code

1. **Report contradictions immediately**, not at the gate. A result that favors the base paper over QSTEG-AE is the most valuable thing you can find, and it is worthless if it arrives late.
2. **Never advance a phase without sign-off.** At a gate, produce a short written summary with the checklist above, then stop and wait.
3. **`src/baseline/` is frozen once P1 gate passes.** Its flaws are evidence.
4. **Two failed attempts → stop and ask.** Write the attempts to `docs/decisions/` first.
5. **Time-box the training tasks** (P1.3, P4.2, P4.3). If a training run exceeds its budget, escalate with the fallback option rather than burning the week.
6. **No number without a seed, no claim without an artifact.** See `CLAUDE.md` invariants.

## Critical path

```
P1.1 → P1.6 (collapse curve)  ─┐
P2.2 (Cascade) → P2.4 (PA) → E1 ─┤→ GATE P2 → the paper is viable
P4.3 (detectors reproduce) → E4 ─┘→ GATE P4 → the stego chapter is viable
```

Everything else is parallelizable or deferrable. If the schedule slips, cut in this order: LDPC arm (P2.2), XChaCha comparator (P3.2), learned INN/GAN embedder (P4.2), ALASKA2 generalization (P4.3).
