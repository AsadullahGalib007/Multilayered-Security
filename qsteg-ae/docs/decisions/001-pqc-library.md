# 001 — PQC library: liboqs-python, built without OpenSSL

**Status:** accepted · **Phase:** P0.1 · **Date:** 2026-08-12

## Context

P3.1 needs ML-KEM-768 (FIPS 203) for the hybrid combiner. `CLAUDE.md` invariant 3
forbids hand-rolling it and names `liboqs-python` first, `pqcrypto` as fallback. The
plan (P0.1) anticipated the native build failing and pre-authorised the fallback.

## What actually happened

Two version problems and one build problem.

1. `liboqs-python==0.12.0` (the version I first pinned, from the proposal's era) **is
   not on PyPI at all** — the published line is 0.9.0, then 0.10.0, then 0.16.0.
   Resolution failed outright. Pinned **0.16.0**, the current release.

2. `liboqs-python` does not vendor the native library. On first `import oqs` it
   git-clones liboqs and cmake-builds it into `$HOME/_oqs`. That build **failed**:

   ```
   Could NOT find OpenSSL ... (missing: OPENSSL_CRYPTO_LIBRARY OPENSSL_INCLUDE_DIR)
   ```

   The machine has the `openssl` binary but not `libssl-dev`, and installing it needs
   root.

3. Rather than take the fallback, I built liboqs by hand with `-DOQS_USE_OPENSSL=OFF`.
   liboqs supports this configuration first-class: OpenSSL only supplies optional
   AES/SHA-2/SHA-3 acceleration, and ML-KEM's correctness does not depend on it.
   Build succeeded; `liboqs.so.0.16.0` installed to `$HOME/_oqs/lib`.

## Decision

**Use `liboqs-python` 0.16.0 against a locally built liboqs 0.16.0 with
`OQS_USE_OPENSSL=OFF`.** No fallback to `pqcrypto` — it was not needed.

`pqcrypto==0.4.0` stays declared under the `pqc-fallback` optional-dependency group,
uninstalled, so the escape hatch is one command away on a machine where the native
build cannot be made to work.

## Verification

```
ML-KEM-768 enabled: 1
KEM roundtrip: True | pk 1184  ct 1088  ss 32
```

Sizes match FIPS 203 Table 3 for ML-KEM-768. Encapsulate/decapsulate agree.
Locked in as `tests/test_environment.py::test_mlkem768_roundtrip_and_fips203_sizes`.

## Consequences

- **Reproducibility hazard, mitigated.** The native library is outside `uv.lock`, so
  `uv sync` alone does *not* give a working `oqs`. `scripts/bootstrap_liboqs.sh`
  captures the exact build (idempotent, version-parameterised, defaults to 0.16.0 to
  match the `liboqs-python` pin). It must run before `uv sync` on any new machine,
  and it belongs in CI. Recorded in `README.md`.
- **No AES/SHA hardware acceleration inside liboqs.** Affects ML-KEM keygen/encap
  throughput only. Relevant to E6 (P3.4) performance numbers: if the ML-KEM line in
  that table looks slow, this is why, and the paper should say so rather than report
  it as an inherent ML-KEM cost.
- **API note for P3.1:** liboqs-python 0.16.0 renamed the module functions to
  snake_case — `oqs.is_kem_enabled(...)`, not `oqs.is_KEM_enabled(...)`. Most
  tutorials and older code use the old spelling.
- The version pin in `scripts/bootstrap_liboqs.sh` and the one in `pyproject.toml`
  must be bumped together.
