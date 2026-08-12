"""Reference implementation of the experiment protocol — copy this to start a real one.

Run it::

    python -m experiments._template
    python -m experiments._template --seed 7 --out results/scratch --smoke

The numbers it produces are **synthetic and carry no scientific meaning**. It exists to
prove the plumbing works: seeded RNG, raw data on disk, a figure through `src/viz`, and a
manifest that ties them to a git SHA. Copying it gives a new experiment every guarantee
in `CLAUDE.md` for free.

To make a real experiment from it:

1. rename to `experiments/<experiment_id>.py` and set `EXPERIMENT_ID` to match
2. replace `body()` with the actual work
3. keep `run.record(...)` / `run.report(...)` calls — they are what makes the result
   traceable, and a number that reaches a table without them is unciteable
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from experiments._harness import Run, run
from src.viz import style

EXPERIMENT_ID = "_template"
DESCRIPTION = "Protocol smoke test: seeded RNG, raw artifacts, styled figure, manifest."


def body(ctx: Run) -> None:
    """Generate synthetic data, write it, and plot it. Not science — plumbing."""
    n_points = 12 if ctx.smoke else 60
    n_series = 3
    ctx.record(n_points=n_points, n_series=n_series, note="synthetic data; no meaning")

    # Seeded by the harness before this runs, but a local Generator is better practice
    # than the global one — it makes the dependency on the seed explicit and local.
    rng = np.random.default_rng(ctx.seed)
    x = np.linspace(0.0, 12.0, n_points)
    curves = np.vstack([100.0 / (1.0 + np.exp(x - shift)) for shift in (2.0, 5.0, 8.0)])
    curves = np.clip(curves + rng.normal(0.0, 1.5, curves.shape), 0.0, 100.0)

    # Raw data, never only a plot. Arrays as .npz; the tabular summary as .parquet,
    # which is what the pandas/pyarrow pins in pyproject.toml exist for.
    np.savez_compressed(ctx.path("raw.npz"), x=x, curves=curves)
    frame = pd.DataFrame(
        {
            "x": np.tile(x, n_series),
            "y": curves.ravel(),
            "series": np.repeat([f"series {i + 1}" for i in range(n_series)], n_points),
        }
    )
    frame.to_parquet(ctx.path("data.parquet"), index=False)

    # Every figure goes through src/viz — never inline matplotlib config.
    with style.figure(width=style.WIDTH_1COL, height=2.2) as (fig, ax):
        for i in range(n_series):
            ax.plot(x, curves[i], label=f"series {i + 1}", **style.series(i, n_points=n_points))
        style.finish(ax, xlabel="synthetic x", ylabel="synthetic y (%)")
        style.save(fig, ctx.path("figure"))

    ctx.report(
        final_values=[round(float(v), 3) for v in curves[:, -1]],
        max_value=round(float(curves.max()), 3),
    )


def main(argv: list[str] | None = None) -> None:
    run(EXPERIMENT_ID, DESCRIPTION, body, argv=argv)


if __name__ == "__main__":
    main()
