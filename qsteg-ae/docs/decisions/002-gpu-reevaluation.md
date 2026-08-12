# 002 — GPU re-evaluation after the NVIDIA driver was installed

**Status:** accepted · **Phase:** P0.1 (revisit) · **Date:** 2026-08-12
**Supersedes:** the *rationale* in [`000-environment-pins.md`](000-environment-pins.md) §"Torch 2.6.0 CPU wheels". **The pin itself does not change.**

## Context

Decision 000 pinned CPU wheels because `nvidia-smi` failed — a GeForce 930MX was
present but no driver was loaded. That premise is now false:

```
NVIDIA-SMI 580.173.02   Driver Version: 580.173.02   CUDA Version: 13.0
GPU 0: NVIDIA GeForce 930MX   compute_cap 5.0   2048 MiB
```

Decision 000 listed "fixing the NVIDIA driver" as one of three options for the
CPU-bound training tasks (P1.3b, P4.3). The driver is now fixed, so the option had to
be measured rather than assumed.

## What was measured

`torch==2.6.0+cu118` in a throwaway venv (the project env was not touched).
**cu118 specifically:** the 930MX is compute capability **5.0 (Maxwell)**, and
Maxwell was dropped from the recent CUDA toolkits. cu118 still ships `sm_50` cubins:

```
arch_list: ['sm_50', 'sm_60', 'sm_70', 'sm_75', 'sm_80', 'sm_86', 'sm_37', 'sm_90']
```

Correctness first — same weights and input on both devices:

```
max |cpu - gpu| abs diff: 1.34e-07     (fp32 rounding noise; the GPU computes correctly)
```

Then throughput, on the *actual* `PrepNetwork` stack from
`../deep_steganography.py` (4× `Conv2d(50, 50, 3, padding=1)`), full
forward+backward+Adam step, 30 timed iterations after 5 warmup:

| shape | CPU | CUDA | speedup |
|---|---:|---:|---:|
| 64×64, batch 1 — **the P1.3b workload** | 29.47 ms/step | 21.87 ms/step | **1.35×** |
| 64×64, batch 16 | 486.14 ms/step | 885.96 ms/step | **0.55× (slower)** |
| 256×256, batch 8 | 4928.85 ms/step | 2415.61 ms/step | 2.04× |

Peak VRAM at 256×256 batch 8: **1060 MiB** of ~1746 MiB usable (Xorg and
gnome-shell hold ~250 MiB of the 2048 MiB card permanently — the GPU also drives the
display). Card hit **88 °C** under sustained load, so a long training run will
thermally throttle and the measured speedups are optimistic.

## Decision

**Keep the CPU wheel pin.** The driver fix is real but does not earn the swap:

1. **1.35× on the workload that actually fits.** P1.3b is 64×64×3 at batch 1
   (`deep_steganography.py:350`, "one pair at a time for simplicity"). Trading 2.4 GB
   of CUDA wheels and a reproducibility hazard for 1.35× is a bad trade.
2. **Negative at batch 16.** A 930MX is 384 Maxwell cores on DDR3-class bandwidth;
   at this model size the kernel-launch and transfer overhead dominates and the CPU
   wins outright. Any "just raise the batch size" fix makes it worse, not better.
3. **Determinism.** Invariant 1 is *no number without a seed*. cuDNN picks
   convolution algorithms nondeterministically by default; making CUDA reproducible
   needs `torch.use_deterministic_algorithms(True)` plus `CUBLAS_WORKSPACE_CONFIG`,
   which costs more speed than the 1.35× being bought.
4. **CI runs CPU anyway** (P0.2), so a CUDA-pinned lock would mean the numbers in the
   paper and the numbers in CI come from different kernels.

## What this does *not* resolve

**P4.3 is still blocked, and the driver fix does not unblock it.** Decision 000
flagged SRNet / Ye-Net / Zhu-Net on BOSSBase+BOWS2 as not realistically trainable
here. That is unchanged and now quantified: the detectors train on 512×512 grayscale,
and 256×256 at batch 8 already consumes 1060 MiB of ~1746 MiB usable on a model far
smaller than SRNet. The card is too small, not too slow.

The three options from decision 000 are now two:

- ~~fix the NVIDIA driver~~ — **done, insufficient**
- rent a GPU for P4.3 (and P4.2's learned arm)
- reduce P4.3 scale and say so plainly in the paper

Per plan.md P4.3: *"if they do not reproduce, the detectors are broken and every P_E
number is worthless."* A reduced-scale protocol has to still reproduce published
accuracy on WOW/S-UNIWARD at 0.4 bpp within a few points, or E4 is not reportable.
**This needs an owner decision before P4, not before P1.** It is not on the P1
critical path.

## If the swap is ever wanted

cu118 is the only line that still supports this card. The change is confined to
`[tool.uv.sources]` in `pyproject.toml` (swap the `pytorch-cpu` index for
`https://download.pytorch.org/whl/cu118`) plus a re-lock.
`tests/test_environment.py::test_torch_build_is_coherent_with_hardware` accepts
either build and will verify that a CUDA build can actually reach an `sm_50`-capable
device, so the swap fails loudly rather than silently falling back.
