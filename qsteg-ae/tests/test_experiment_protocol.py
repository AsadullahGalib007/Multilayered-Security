"""P0.2 acceptance: the experiment protocol in `CLAUDE.md` is enforced by the harness.

These tests are the guard on invariants 1 and 2 (*no number without a seed*, *no claim
without an artifact*). If they fail, results produced by any experiment are not
traceable and nothing downstream is citable.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from experiments import _template
from experiments._harness import Run, load_manifest, run

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@pytest.fixture
def result_dir(tmp_path: Path) -> Path:
    """Run the template experiment in smoke mode into a temp dir."""
    out = tmp_path / "_template"
    _template.main(["--out", str(out), "--smoke"])
    return out


def test_template_writes_manifest_with_git_sha_and_seed(result_dir: Path) -> None:
    """The plan's literal P0.2 acceptance criterion."""
    manifest = load_manifest(result_dir / "manifest.json")

    assert manifest["experiment_id"] == "_template"
    assert manifest["seed"] == 20240816
    assert SHA_RE.match(
        manifest["git"]["commit"]
    ), f"manifest git commit is not a full SHA: {manifest['git']['commit']!r}"


def test_manifest_carries_every_field_the_protocol_requires(result_dir: Path) -> None:
    manifest = load_manifest(result_dir / "manifest.json")

    # CLAUDE.md: "git commit SHA, seed, all params, package versions, wall time, hostname"
    assert manifest["host"]["hostname"]
    assert isinstance(manifest["wall_time_s"], float)
    assert manifest["params"]["n_points"] == 12, "smoke mode should reduce the scale"
    assert manifest["status"] == "ok"
    assert manifest["smoke"] is True

    versions = manifest["packages"]
    for package in ("qiskit", "torch", "numpy", "cryptography"):
        assert versions[package] != "not installed"


def test_raw_data_is_written_not_only_a_plot(result_dir: Path) -> None:
    """Protocol step 4: raw data as .parquet or .npz — never only a figure."""
    assert (result_dir / "raw.npz").is_file()
    assert (result_dir / "data.parquet").is_file()
    assert (result_dir / "figure.pdf").is_file()
    assert (result_dir / "figure.png").is_file()


def test_same_seed_reproduces_identical_results(tmp_path: Path) -> None:
    """Invariant 1 is worthless if the seed does not actually determine the output."""
    import numpy as np

    first, second = tmp_path / "a", tmp_path / "b"
    _template.main(["--out", str(first), "--smoke", "--seed", "4242"])
    _template.main(["--out", str(second), "--smoke", "--seed", "4242"])

    a = np.load(first / "raw.npz")
    b = np.load(second / "raw.npz")
    np.testing.assert_array_equal(a["curves"], b["curves"])

    assert load_manifest(first / "manifest.json")["metrics"] == (
        load_manifest(second / "manifest.json")["metrics"]
    )


def test_different_seed_changes_results(tmp_path: Path) -> None:
    """The counterpart: if the seed changes nothing, it is not wired to the RNG."""
    import numpy as np

    first, second = tmp_path / "a", tmp_path / "b"
    _template.main(["--out", str(first), "--smoke", "--seed", "1"])
    _template.main(["--out", str(second), "--smoke", "--seed", "2"])

    a = np.load(first / "raw.npz")["curves"]
    b = np.load(second / "raw.npz")["curves"]
    assert not np.array_equal(a, b)


def test_failed_run_still_writes_a_manifest(tmp_path: Path) -> None:
    """A crashed run that leaves no trace looks identical to one that never happened."""

    def explode(ctx: Run) -> None:
        ctx.record(attempted=True)
        raise RuntimeError("deliberate failure")

    out = tmp_path / "boom"
    with pytest.raises(RuntimeError, match="deliberate failure"):
        run("boom", "always fails", explode, argv=["--out", str(out)])

    manifest = load_manifest(out / "manifest.json")
    assert manifest["status"] == "failed"
    assert manifest["params"]["attempted"] is True


def test_manifest_is_valid_json_and_stable_key_order(result_dir: Path) -> None:
    """Sorted keys keep P5.3's clean-room diff readable instead of noisy."""
    text = (result_dir / "manifest.json").read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert list(parsed) == sorted(parsed)
