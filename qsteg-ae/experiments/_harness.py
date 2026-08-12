"""The experiment protocol from `CLAUDE.md`, implemented once.

Every experiment script imports this rather than reimplementing it, so that *no number
without a seed* and *no claim without an artifact* are properties of the harness instead
of things each script has to remember.

What it guarantees for every run:

1. an explicit seed, recorded in the manifest and applied to `random`, `numpy`, and
   `torch` before the experiment body runs (invariant 1)
2. `results/<id>/manifest.json` carrying git SHA, dirty flag, seed, every parameter,
   resolved package versions, wall time, and hostname (invariant 2)
3. `--smoke` for a fast reduced-scale run, so CI can execute the real code path

Underscore-prefixed so it is never mistaken for an experiment: `experiments/` holds one
module per experiment ID, and this is not one.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import socket
import subprocess
import sys
import time
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any

DEFAULT_SEED = 20240816

# Recorded in every manifest. The point is not to pin these again — `uv.lock` does that —
# but to make a manifest self-describing when it is read back months later next to a
# number in the paper.
_TRACKED_PACKAGES = (
    "qiskit",
    "qiskit-aer",
    "cryptography",
    "pycryptodome",
    "liboqs-python",
    "torch",
    "numpy",
    "scipy",
    "scikit-image",
    "pandas",
    "matplotlib",
)


def _git(*args: str) -> str | None:
    """Run a git command in the repo, or return None if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def _package_versions() -> dict[str, str]:
    versions = {}
    for name in _TRACKED_PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def seed_everything(seed: int) -> None:
    """Seed every RNG that could reach a result. Called by `run()` before the body."""
    random.seed(seed)
    try:
        import numpy as np

        # Legacy global RNG on purpose, despite NPY002. `src/baseline/` is a frozen port
        # of the base paper and calls np.random.* directly; invariant 8 forbids rewriting
        # it to take a Generator, so the global seed is the only way its numbers become
        # reproducible. New code should still use np.random.default_rng(ctx.seed).
        np.random.seed(seed)  # noqa: NPY002
    except ImportError:  # pragma: no cover - numpy is a hard dependency
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:  # pragma: no cover - torch is a hard dependency
        pass


@dataclass
class Run:
    """A single experiment run: where to write, what seed, and what to record.

    The experiment body receives one of these. Anything it puts in `params` or `metrics`
    lands in the manifest, so a number in the paper can always be traced back to the run
    that produced it.
    """

    experiment_id: str
    out_dir: Path
    seed: int
    smoke: bool
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)

    def record(self, **params: Any) -> None:
        """Record experiment parameters for the manifest."""
        self.params.update(params)

    def report(self, **metrics: Any) -> None:
        """Record headline metrics for the manifest.

        Raw data still belongs in a `.parquet`/`.npz` beside it — the manifest is an
        index, never the only copy of a result.
        """
        self.metrics.update(metrics)

    def path(self, name: str) -> Path:
        """A path inside this run's output directory."""
        self.out_dir.mkdir(parents=True, exist_ok=True)
        return self.out_dir / name


def _write_manifest(run: Run, wall_time_s: float, status: str) -> Path:
    sha = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain")
    manifest = {
        "experiment_id": run.experiment_id,
        "status": status,
        "seed": run.seed,
        "smoke": run.smoke,
        "git": {
            "commit": sha,
            # A number generated from uncommitted code is not reproducible. Recording it
            # is the honest option; P5.3's clean-room re-run is what clears it.
            "dirty": bool(dirty) if dirty is not None else None,
        },
        "params": run.params,
        "metrics": run.metrics,
        "wall_time_s": round(wall_time_s, 3),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "packages": _package_versions(),
    }
    run.out_dir.mkdir(parents=True, exist_ok=True)
    path = run.out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_parser(experiment_id: str, description: str) -> argparse.ArgumentParser:
    """The argument surface every experiment shares."""
    parser = argparse.ArgumentParser(
        prog=f"python -m experiments.{experiment_id}", description=description
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"RNG seed, recorded in the manifest (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"output directory (default: results/{experiment_id})",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="fast reduced-scale run; exercises the same code path for CI",
    )
    return parser


@contextmanager
def _timed() -> Iterator[Callable[[], float]]:
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


def run(
    experiment_id: str,
    description: str,
    body: Callable[[Run], None],
    argv: list[str] | None = None,
    extra_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> Path:
    """Execute `body` under the protocol and return the manifest path.

    A failing body still writes a manifest, marked `"status": "failed"`, before the
    exception propagates — a crashed run that leaves no trace is indistinguishable from
    one that never happened, and that ambiguity is how phantom numbers survive.
    """
    parser = build_parser(experiment_id, description)
    if extra_args is not None:
        extra_args(parser)
    args = parser.parse_args(argv)

    out_dir = args.out if args.out is not None else Path("results") / experiment_id
    run_ctx = Run(
        experiment_id=experiment_id,
        out_dir=Path(out_dir),
        seed=args.seed,
        smoke=args.smoke,
    )
    run_ctx.record(**{k: v for k, v in vars(args).items() if k not in {"seed", "out", "smoke"}})

    seed_everything(args.seed)

    with _timed() as elapsed:
        try:
            body(run_ctx)
        except Exception:
            _write_manifest(run_ctx, elapsed(), status="failed")
            raise
        manifest_path = _write_manifest(run_ctx, elapsed(), status="ok")

    print(f"[{experiment_id}] wrote {manifest_path}")
    return manifest_path


def load_manifest(path: str | Path) -> Mapping[str, Any]:
    """Read a manifest back. Used by tests and by the P5.3 reproducibility pass."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
