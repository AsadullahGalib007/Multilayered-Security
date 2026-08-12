"""P0.1 acceptance: the pinned environment imports and the crypto primitives work.

This suite is the guard on CLAUDE.md invariant 3 (vetted libraries only). If it
fails, nothing downstream is trustworthy — fix the environment before running any
experiment.
"""

import sys

import pytest


def test_python_version() -> None:
    assert (3, 11) <= sys.version_info < (3, 13), "pyproject pins >=3.11,<3.13"


def test_qiskit_aer_imports_and_simulates() -> None:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    # Bell pair: the primitive the E91 layer is built from.
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    counts = AerSimulator().run(qc, shots=1024, seed_simulator=20240816).result().get_counts()
    assert set(counts) <= {"00", "11"}, f"Bell state leaked into {set(counts)}"
    assert sum(counts.values()) == 1024


def test_torch_imports() -> None:
    import torch

    torch.manual_seed(20240816)
    x = torch.randn(4, 4)
    assert (x @ torch.eye(4)).allclose(x)


def test_torch_build_is_coherent_with_hardware() -> None:
    """The CPU pin is a measured choice, not a hardware limitation — see decision 002.

    Asserts the build and the machine agree, rather than hardcoding CPU. A CUDA wheel
    that cannot reach a usable device is a broken environment and must fail here, not
    three phases later inside a training run.
    """
    import torch

    if "+cu" in torch.__version__:
        # Deliberate swap (decision 002 documents how). Verify it actually works.
        assert torch.cuda.is_available(), (
            f"torch {torch.__version__} is a CUDA build but no device is reachable — "
            "check the driver before trusting any number produced on this env"
        )
        capability = torch.cuda.get_device_capability(0)
        assert f"sm_{capability[0]}{capability[1]}" in torch.cuda.get_arch_list(), (
            f"torch {torch.__version__} ships {torch.cuda.get_arch_list()} but this "
            f"device is sm_{capability[0]}{capability[1]}; kernels will fail at launch. "
            "Maxwell (sm_50) needs the cu118 wheels — see docs/decisions/002."
        )
    else:
        assert "+cpu" in torch.__version__, (
            "pyproject pins CPU wheels via [tool.uv.sources]; an unrecognised build "
            "here means the lock drifted. Update docs/decisions/ if this was deliberate."
        )


def test_liboqs_available() -> None:
    """Requires scripts/bootstrap_liboqs.sh to have run. See decision 001."""
    oqs = pytest.importorskip("oqs", reason="liboqs not built; run scripts/bootstrap_liboqs.sh")
    assert oqs.is_kem_enabled("ML-KEM-768"), "ML-KEM-768 (FIPS 203) not compiled into liboqs"


def test_mlkem768_roundtrip_and_fips203_sizes() -> None:
    oqs = pytest.importorskip("oqs", reason="liboqs not built; run scripts/bootstrap_liboqs.sh")

    with oqs.KeyEncapsulation("ML-KEM-768") as kem:
        public_key = kem.generate_keypair()
        ciphertext, shared_secret_enc = kem.encap_secret(public_key)
        shared_secret_dec = kem.decap_secret(ciphertext)

    assert shared_secret_enc == shared_secret_dec
    # FIPS 203 Table 3, ML-KEM-768.
    assert len(public_key) == 1184
    assert len(ciphertext) == 1088
    assert len(shared_secret_enc) == 32


def test_aes_gcm_available_from_cryptography() -> None:
    """AEAD comes from `cryptography`, never hand-rolled (invariant 3)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = bytes(range(32))
    nonce = bytes(12)
    aead = AESGCM(key)
    ciphertext = aead.encrypt(nonce, b"payload", b"aad")
    assert aead.decrypt(nonce, ciphertext, b"aad") == b"payload"


def test_hkdf_available_from_cryptography() -> None:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF

    derived = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"salt", info=b"info").derive(b"ikm")
    assert len(derived) == 32


def test_numerics_and_imaging_stack() -> None:
    import numpy
    import pandas
    import pyarrow  # noqa: F401  — parquet backend for the experiment protocol
    import scipy  # noqa: F401
    import skimage  # noqa: F401

    assert numpy.__version__.startswith("1.26")
    assert pandas.__version__.startswith("2.2")


def test_matplotlib_uses_headless_backend() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure()
    plt.close(fig)
