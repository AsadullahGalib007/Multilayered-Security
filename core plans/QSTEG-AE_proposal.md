# Incremental Research Proposal — QSTEG-AE

**Base paper:** Sykot et al., *Multi-Layered Security System: Integrating Quantum Key Distribution with Classical Cryptography to Enhance Steganographic Security*, arXiv:2408.06964v1 (NSU, 2024).

**Target:** Q2 journal (or top-tier workshop/conference). Q1 reachable if finite-key + steganalysis arms both land.

---

## 1. Base paper methodology (extracted)

Pipeline, linear, no feedback:

```
E91 (Qiskit singlet circuits)
  → basis measurement {Z, (X+Z)/√2, X} Alice / {(X+Z)/√2, X, (X−Z)/√2} Bob
  → CHSH test on mismatched-basis subset (Eve detection)
  → sifted key from matched bases (anti-correlated outcomes)
  → SHA-256 → 256-bit key H
  → AES(H) encrypts stego image
  → stego image made earlier by Baluja-style hiding CNN (secret + cover)
  → classical channel → AES decrypt → revealing CNN → secret out
```

Formalism: `C = AES_enc(I, H'(E91_key))`, `I = AES_dec(C, H)`.

Reported evaluation:

| Metric | Value |
|---|---|
| Entropy of cipher | 7.984 – 7.9995 (8.0 ideal) |
| NPCR | 99.54 – 99.82 % |
| UACI | 54.44 – 57.74 % |
| Key gen rate | 1.59 → 12.24 bps (25 → 500 singlets) |
| Key length | 7 → 106 bits |
| Enc/dec time | ~1.5 ms / 1.75 ms avg |
| Extra | histograms, 1-bit key sensitivity |

Stated future scope: quantum error correction, noisy channels, hybrid quantum-classical, better stego nets.

---

## 2. Gap analysis — seven attackable defects

Ordered by publication leverage. Each is a paper section.

### G1 — SHA-256 is not privacy amplification (**critical**)
Paper does sifting → hash → done. Missing: parameter estimation, **information reconciliation**, **privacy amplification with leftover-hash bound**, finite-key ε-security. SHA-256 is a fixed non-2-universal map; it gives no bound on Eve's smooth min-entropy about the output. Standard QKD post-processing is five subprotocols, not one [5].

### G2 — Protocol breaks at QBER > 0 (**critical, empirical**)
No error correction ⇒ Alice's and Bob's sifted keys differ under any real noise ⇒ different SHA digests ⇒ AES decryption fails completely. All results are noiseless-simulator artifacts. Real BBM92 runs sit at QBER ≈ 4.5 % [7]. This is the single most damaging and most demonstrable flaw.

### G3 — UACI numerically wrong (**verified**)
Ideal-cipher expectation, derived and reproduced numerically:

```
E[NPCR] = (1 − 2^-8)·100 = 99.6094 %
E[UACI] = Σ_{i=1..255} i(i+1) / (255·256²) ·100 = 33.4635 %
```

Monte-Carlo over independent uniform 8-bit images: NPCR 99.60–99.68, UACI 33.36–33.56. Paper's 54–57 % means they computed **plain vs. cipher**, not **cipher(P) vs. cipher(P′)** with a 1-pixel plaintext flip. NPCR/UACI as printed measure nothing about differential resistance. Correct test procedure and critical values are in Wu et al. [1, prev-metrics]; these statistics are necessary-not-sufficient anyway [3, 5 prev-metrics].

### G4 — AES mode unspecified, no AEAD
No mode, no IV/nonce, no MAC. Claims "integrity" while providing none. If ECB, the flat histograms are unearned. Ciphertext malleable ⇒ attacker flips bits in the stego payload undetected.

### G5 — Hide-then-encrypt destroys covertness
Encrypting the stego image yields high-entropy noise on the wire. An observer sees uniform garbage, not an innocuous photo. The steganographic layer buys nothing against a warden. Order must invert.

### G6 — Zero steganalysis
No SRNet / Ye-Net / Zhu-Net / SRM evaluation, no PSNR/SSIM of stego vs cover, no bpp/detectability curve, no robustness under JPEG/noise/resize. Modern detectors hit 99 %+ on WOW/S-UNIWARD at 0.2–0.4 bpp [3, 5, 9 stego]. An unevaluated stego layer is an unclaimed layer.

### G7 — Key economics ignored + self-overlap
12.24 bps peak. One 256-bit AES key ≈ 21 s of QKD. No key-consumption model, no ratchet, no refresh policy, no PQC fallback when the quantum link drops. Separately: the identical key-rate table (1.59 / 5.37 / 10.52 / 12.24 bps; 7 / 25 / 57 / 106 bits) is already republished in a 2025 Qiskit-E91 simulation paper [1, qiskit] — the rate numbers are spent as a novelty claim.

---

## 3. Proposed methodology — **QSTEG-AE**
*Entropy-Accounted Hybrid Quantum-Classical Covert Channel*

Five modules. Each maps to one gap; each is independently ablatable.

### M1 — Composable post-processing chain (fixes G1, G2)
Replace `SHA-256(sifted)` with:

```
raw → sifting → parameter estimation (QBER Q, CHSH S)
    → information reconciliation: Cascade or rate-adaptive LDPC, leakage ℓ_EC measured
    → error verification: 2-universal hash tag, ε_cor
    → privacy amplification: Toeplitz matrix, output length
        ℓ ≤ n[1 − h(Q_x)] − ℓ_EC − log₂(2/ε_cor) − 2log₂(1/(2ε_PA))
    → composable ε-secure key
```

Report ε_cor, ε_sec, ε_PA explicitly. Toeplitz PA is the baseline; note spinal-code joint IR-PA as a throughput variant [6, pp]. Reference implementations for the full chain exist [1, 2, 5 pp] and for E91 specifically [6, qkd-sim].

**Deliverable claim:** first E91-plus-steganography stack with composable finite-key accounting instead of a bare hash.

### M2 — Hybrid QKD ⊕ PQC key combiner (fixes G7)
```
K = HKDF-Extract-then-Expand( K_QKD ‖ K_ML-KEM ‖ K_ECDH , salt, info )
```
IND-CCA-secure 3-way combiner; secure if **any one** component survives. ML-KEM-768 (FIPS 203) carries the load when the quantum link is down or key-starved; QKD supplies information-theoretic material when available. Precedent and proof techniques: [1, 2, 3, 5, 9 hybrid]. Finite-key-aware hybrid is *very* recent and thin [8, hybrid] — room to sit.

**Deliverable claim:** crypto-agile key supply that degrades gracefully at 12 bps instead of stalling.

### M3 — AEAD with binding (fixes G4)
`AES-256-GCM` (and `XChaCha20-Poly1305` as comparator). Per-message nonce from a ratchet counter, never reused. **AAD = (cover ID, embedding parameters, payload length, sequence number)** — binds ciphertext to its embedding context, so a warden cannot splice payloads between covers. Integrity now real, not asserted.

### M4 — Encrypt-then-embed inversion (fixes G5)
```
secret → AEAD encrypt → ciphertext + tag
       → adaptive-cost embedding into cover (HILL / S-UNIWARD via STC, and an INN/GAN hiding net as the learned arm)
       → stego image, statistically an ordinary photo, transmitted in clear
```
Ciphertext is uniform ⇒ ideal payload for provably-secure-style embedding; the channel now looks innocuous [6, 5 pss]. Optional: rejection-sampling PSS variant for a formal indistinguishability argument.

### M5 — Key-budget scheduler (fixes G7)
Treat QKD output as a **rate-limited resource**. HKDF ratchet: one QKD block seeds a chain, per-image keys derived, re-seed on budget/time policy. New metric:

```
KCE = secure QKD bits consumed / secret payload bits delivered
```
Plot KCE vs. covert capacity vs. detectability. Nobody in this sub-literature reports this.

---

## 4. Experimental design

### E1 — QBER sweep (headline figure)
Depolarizing channel, p ∈ [0,1] → QBER 0 → 12 %. Plot for base paper vs QSTEG-AE:
- key agreement rate (Alice ≡ Bob)
- **decryption success rate** — base paper collapses to ~0 the moment QBER > 0; QSTEG-AE stays 1.0 up to the EC threshold
- secret key length after PA

This single figure justifies the paper.

### E2 — Finite-key scaling
ℓ_secure vs block size n ∈ [10³, 10⁷] at fixed ε = 10⁻¹⁰, Q ∈ {1,3,5,8} %. Show where the base paper's 106-bit "key" lands (answer: below any useful ε-security threshold).

### E3 — Corrected differential analysis
NPCR/UACI computed properly: cipher(P) vs cipher(P′), P′ = P with one pixel LSB flipped. Report against critical values, not against "close to 100 %". Include the base paper's numbers recomputed both ways as a correction table.

### E4 — Steganalysis
Detectors: SRM+ensemble, Ye-Net, Zhu-Net, SRNet. Payloads 0.05–0.5 bpp. BOSSBase 1.01 + BOWS2 + ALASKA2. Report P_E (min avg detection error) vs bpp for: base paper's encrypted-stego, QSTEG-AE encrypt-then-embed, and plain cover baselines.

### E5 — Imperceptibility & robustness
PSNR, SSIM, LPIPS on stego. Robustness: JPEG QF 50/75/95, Gaussian σ ∈ {1,3,5}, resize ±25 %, cropping 5 %. Report payload BER post-attack.

### E6 — Performance
Throughput, latency, memory: QSTEG-AE vs (a) base paper, (b) PQC-only ML-KEM baseline, (c) classical ECDH baseline. Include PA Toeplitz cost — the part everyone omits.

### E7 — Ablation
Drop one module at a time (M1…M5), report the security/perf delta. Reviewers ask for this; have it pre-built.

### E8 — Attack suite
Known-plaintext, chosen-plaintext, ciphertext tampering (verify GCM rejects), nonce-reuse simulation (show what breaks without M3), intercept-resend on the quantum link (CHSH S drops below 2√2), and a warden model for the stego layer.

---

## 5. Novelty positioning — crosscheck against 2024-2026 literature

| Component | Prior art | QSTEG-AE delta |
|---|---|---|
| Composable finite-key PA | Mature in CV-QKD [1,2,3,7 pp], surveyed [5 pp] | Not applied to *E91 + steganography* stacks; the sub-literature still uses bare SHA |
| Hybrid QKD+PQC combiner | Active, FPGA-proven [1,2 hybrid], triple-hybrid TLS/IPsec [5 hybrid], NIST-standard schemes [9 hybrid] | None of it feeds a **covert/steganographic** channel; finite-key-aware hybrid barely exists [8 hybrid] |
| Encrypt-then-embed AEAD | PSS theory strong [6,5,2 pss]; ECC public-key PSS [3,10 pss] | PSS literature is LLM/text-heavy; image + quantum key supply not covered |
| Deep steganalysis eval | SRNet/Zhu-Net/Ye-Net standard [3,10,1 stego] | Never applied to QKD-keyed image stego papers — free win |
| Metric correction | NPCR/UACI critiques exist [1,3,5 metrics] | Chance to publish a concrete correction of a cited 2024 arXiv result |
| E91 Qiskit key rates | Already published twice, same numbers [1 qiskit] | Do **not** re-report; treat as settled baseline |

**Risk:** each individual piece exists somewhere. **Mitigation:** the contribution is the *integrated, correctly-accounted* stack plus the QBER-collapse result (E1) and the corrected-metrics table (E3). Frame as "systematization + repair + extension," not "novel primitive." That framing survives review; "novel hybrid" would not.

---

## 6. Paper skeleton

1. Intro — harvest-now-decrypt-later + covert channels
2. Background: E91, finite-key security, AEAD, adaptive stego, PQC
3. **Analysis of the existing pipeline** — G1…G7 with the corrected NPCR/UACI table (this is the hook)
4. QSTEG-AE: M1–M5, threat model (Eve on quantum link, Warden on classical link, active tamperer), security argument
5. Implementation: Qiskit Aer + noise models, liboqs/pqcrypto ML-KEM, cryptography/PyCA GCM, PyTorch stego + steganalysis
6. Evaluation: E1–E8
7. Discussion, limitations (simulator not hardware; state it plainly), future work
8. Conclusion

## 7. Venue map

- **Q1 stretch:** IEEE TIFS, IEEE IoT-J, npj Quantum Information (if finite-key rigor is real)
- **Q2 realistic:** IEEE Access, Quantum Information Processing, Journal of Information Security and Applications, EPJ Quantum Technology, Scientific Reports
- **Conference:** QCNC, ICTON, IEEE QCE, ARES, ICISSP
- **Fast validation:** arXiv preprint first; the corrected-metrics section alone draws citations

## 8. Execution order (12–16 weeks)

| Phase | Weeks | Output |
|---|---|---|
| P1 | 1–2 | Reproduce base paper in Qiskit; confirm the metric errors; freeze baseline numbers |
| P2 | 3–5 | M1 post-processing chain (Cascade/LDPC + Toeplitz PA + ε accounting) → E1, E2 |
| P3 | 6–7 | M2 hybrid combiner + M3 AEAD + M5 scheduler → E6, E8 |
| P4 | 8–11 | M4 encrypt-then-embed + steganalysis suite → E4, E5 |
| P5 | 12–13 | E3 corrected metrics, E7 ablation |
| P6 | 14–16 | Write, internal review, submit |

**Kill criterion:** if E1 shows the base pipeline survives noise (it will not), drop G2 and lead with G3+G5 instead.

---

## References

**Post-processing / finite-key:**
[1 pp] [Data postprocessing for the one-way heterodyne protocol under composable finite-size security](https://consensus.app/papers/details/4b937c104e7a5c5abbf6d88e245266b1/?utm_source=claude_desktop) (Mountogiannakis et al., 2022, Physical Review A, 12 citations)
[2 pp] [Composably secure data processing for Gaussian-modulated continuous-variable quantum key distribution](https://consensus.app/papers/details/b61bb33e4e8f5a9fb857d8cabc535ce7/?utm_source=claude_desktop) (Mountogiannakis et al., 2021, Physical Review Research, 23 citations)
[3 pp] [Composable security of CV-MDI-QKD with secret key rate and data processing](https://consensus.app/papers/details/7b4065ceba435f6e85fcfac31a5eea0f/?utm_source=claude_desktop) (Papanastasiou et al., 2023, Scientific Reports, 17 citations)
[5 pp] [An Overview of Postprocessing in Quantum Key Distribution](https://consensus.app/papers/details/5b4e9b3d130658f4af32bb74cfb54164/?utm_source=claude_desktop) (Luo et al., 2024, Mathematics, 17 citations)
[6 pp] [Joint Information Reconciliation-Privacy Amplification Scheme for CV-QKD](https://consensus.app/papers/details/6aabe824346f5ad5a800b4effa7ca503/?utm_source=claude_desktop) (Zhang et al., 2025, Journal of Lightwave Technology, 0 citations)
[7 pp] [Finite-Size Security for Discrete-Modulated Continuous-Variable Quantum Key Distribution Protocols](https://consensus.app/papers/details/97b283e788085128b31bbbb07e190430/?utm_source=claude_desktop) (Kanitschar et al., 2023, PRX Quantum, 43 citations)

**Hybrid QKD + PQC:**
[1 hybrid] [Hybrid Keys in Practice: Combining Classical, Quantum and Post-Quantum Cryptography](https://consensus.app/papers/details/9eaa4162114253f2995adde8080a2f70/?utm_source=claude_desktop) (Ricci et al., 2024, IEEE Access, 61 citations)
[2 hybrid] [Experimental Integration of Quantum Key Distribution and Post-Quantum Cryptography in a Hybrid Quantum-Safe Cryptosystem](https://consensus.app/papers/details/c8e74b5fb50958848d5d70d2217bb8e0/?utm_source=claude_desktop) (Garms et al., 2024, Advanced Quantum Technologies, 47 citations)
[3 hybrid] [Quantum secure communication using hybrid post-quantum cryptography and quantum key distribution](https://consensus.app/papers/details/006df76eb0c859edafbb343a4bcb9b96/?utm_source=claude_desktop) (Aquina et al., 2024, ICTON, 16 citations)
[5 hybrid] [Enhanced Network Security Protocols for the Quantum Era](https://consensus.app/papers/details/405a6ae946f153d495be6ec6ab67e02a/?utm_source=claude_desktop) (Rubio García et al., 2025, IEEE JSAC, 29 citations)
[8 hybrid] [Combined Quantum and Post-Quantum Security Performance Under Finite Keys](https://consensus.app/papers/details/c3cef30d259d5bbd9398cccc0276a127/?utm_source=claude_desktop) (Gupta et al., 2025, QCNC 2026, 2 citations)
[9 hybrid] [Hybrid Schemes of NIST Post-Quantum Cryptography Standard Algorithms and Quantum Key Distribution](https://consensus.app/papers/details/5d096fa2a1ec53858e70cda3d1c5f9e2/?utm_source=claude_desktop) (Chen, 2025, ArXiv, 1 citation)

**Steganalysis / stego:**
[1 stego] [Image steganalysis using deep learning models](https://consensus.app/papers/details/4cd5c08cb0a6557796433bef70ef8744/?utm_source=claude_desktop) (Kuznetsov et al., 2023, Multimedia Tools and Applications, 12 citations)
[3 stego] [Depth-Wise Separable Convolutions and Multi-Level Pooling for an Efficient Spatial CNN-Based Steganalysis](https://consensus.app/papers/details/743230cc47ee505c89c1fb22b477ff19/?utm_source=claude_desktop) (Zhang et al., 2019, IEEE TIFS, 361 citations)
[5 stego] [A generalized image steganalysis approach via decision level fusion of deep models](https://consensus.app/papers/details/aa3eabece05b5fc8b5d1073d0f144dc9/?utm_source=claude_desktop) (Swarnkar et al., 2023, Multimedia Tools and Applications, 3 citations)
[9 stego] [Enhancing Secret Data Detection Using Convolutional Neural Networks With Fuzzy Edge Detection](https://consensus.app/papers/details/009c4e6c7cd35a81a2c07d6346e06cf3/?utm_source=claude_desktop) (De La Croix et al., 2023, IEEE Access, 25 citations)
[10 stego] [Deep Learning Hierarchical Representations for Image Steganalysis](https://consensus.app/papers/details/ee1b3693238a566e9501df5ca4d2e9af/?utm_source=claude_desktop) (Ye et al., 2017, IEEE TIFS, 741 citations)

**Provably secure steganography:**
[2 pss] [Provably Secure Steganography Based on List Decoding](https://consensus.app/papers/details/1a9cee431e165d68a9bb592d59f8ca27/?utm_source=claude_desktop) (Pang et al., 2026, ArXiv, 0 citations)
[3 pss] [Provably Secure Public-Key Steganography Based on Admissible Encoding](https://consensus.app/papers/details/a5c2f1d637b35b3fbef5207a40ace559/?utm_source=claude_desktop) (Zhang et al., 2025, IEEE TIFS, 5 citations)
[5 pss] [A Framework for Designing Provably Secure Steganography](https://consensus.app/papers/details/1294aa6921a652278096aafda4ca8532/?utm_source=claude_desktop) (Liao et al., 2025, 14 citations)
[6 pss] [Provably Secure Steganography](https://consensus.app/papers/details/ea61ae4d11ab5e08ae2344c17a1bb94c/?utm_source=claude_desktop) (Hopper et al., 2002, IEEE Transactions on Computers, 254 citations)
[10 pss] [Provably Secure Public-Key Steganography Based on Elliptic Curve Cryptography](https://consensus.app/papers/details/4bb0aafd4d3e58caad3d789334fe3964/?utm_source=claude_desktop) (Zhang et al., 2024, IEEE TIFS, 20 citations)

**Metric critiques:**
[1 metrics] [NPCR and UACI Randomness Tests for Image Encryption](https://consensus.app/papers/details/93af08eb4b6a5b2888855707a7e0227a/?utm_source=claude_desktop) (Wu et al., 2011, 1438 citations)
[2 metrics] [Cryptanalysis of a Chaotic Image Encryption Algorithm Based on Information Entropy](https://consensus.app/papers/details/ee93c32a0ef851d6838e46154e3e6ffd/?utm_source=claude_desktop) (Li et al., 2018, IEEE Access, 199 citations)
[3 metrics] [Depreciating Motivation and Empirical Security Analysis of Chaos-Based Image and Video Encryption](https://consensus.app/papers/details/77efdaae62ed5187b758fff2dc92a89d/?utm_source=claude_desktop) (Preishuber et al., 2018, IEEE TIFS, 218 citations)
[4 metrics] [Image Encryption Algorithms: A Survey of Design and Evaluation Metrics](https://consensus.app/papers/details/5a65f62b6c075943b69df4f7430b01a7/?utm_source=claude_desktop) (Alghamdi et al., 2024, J. Cybersecur. Priv., 81 citations)
[5 metrics] [Role of NPCR and UACI tests in security problems of chaos based image encryption algorithms](https://consensus.app/papers/details/9f62e4708aa85e0c81606cb5dc3bcd6e/?utm_source=claude_desktop) (Özkaynak, 2017, UBMK, 32 citations)

**E91 / entanglement QKD baselines:**
[1 qiskit] [Simulation of E91 Quantum Key Distribution Protocol Using Qiskit](https://consensus.app/papers/details/ace85ca0bdf254e1a863647317a40fe3/?utm_source=claude_desktop) (Kadir et al., 2025, COMPAS, 0 citations) — *identical key-rate table to the base paper*
[2 qkd] [Secure quantum key distribution with realistic devices](https://consensus.app/papers/details/514a3e119116586db9458ebe49cdcc94/?utm_source=claude_desktop) (Xu et al., 2020, Reviews of Modern Physics, 1170 citations)
[6 qkd-sim] [Simulation of an entanglement-based quantum key distribution protocol](https://consensus.app/papers/details/53ec55077ca8501bbeaa4b65a72d2c2f/?utm_source=claude_desktop) (Mariani et al., 2024, EPJ Plus, 8 citations) — *E91 with EC + PA implemented; closest prior art to M1*
[7 qkd] [Experimental Design and Performance Simulation of Core Components for BBM92 Entanglement-Based QKD](https://consensus.app/papers/details/29d21f541f9d533daa977b21cd7f4068/?utm_source=claude_desktop) (Cadena et al., 2026, IEEE Internet Computing, 0 citations) — *QBER 4.5 %, 5.43 bps realistic reference*
[8 qkd] [Design and simulation of secure data center intra-connectivity using entangled QKD](https://consensus.app/papers/details/9a92b7dbf6355a79ad2cb4778885d53f/?utm_source=claude_desktop) (Mehic et al., 2026, Quantum Information Processing, 1 citation) — *full per-block PA accounting template*
[1 e91-nm] [Use of Non-Maximal entangled state for free space BBM92 quantum key distribution protocol](https://consensus.app/papers/details/8948757c5fc55323a9c41845875932e5/?utm_source=claude_desktop) (Biswas et al., 2023, 2 citations) — *E91 key rate low because CHSH eats the qubits; supports M5*
