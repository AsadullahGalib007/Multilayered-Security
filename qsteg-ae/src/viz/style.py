"""The single figure style for QSTEG-AE. Every figure in the paper comes through here.

`CLAUDE.md`: *"Matplotlib for figures. One style file, `src/viz/style.py`, used
everywhere."* Experiment scripts must not touch `matplotlib.rcParams` themselves — if a
figure needs something this module cannot express, add it here so every figure gets it.

Usage::

    from src.viz import style

    with style.figure(width=style.WIDTH_1COL, height=2.2) as (fig, ax):
        for i, (label, xs, ys) in enumerate(series):
            ax.plot(xs, ys, label=label, **style.series(i))
        style.finish(ax, xlabel="QBER (%)", ylabel="Decryption success (%)")
    style.save(fig, "results/e1_qber_sweep/qber_collapse")

Palette provenance and the validator output are in
`docs/decisions/003-figure-style.md`. **Do not edit a hex here without re-running the
validator and updating that record** — the slot order is the colorblind-safety
mechanism, not decoration.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

# ── surfaces and ink ──────────────────────────────────────────────────────────────
# Figures print on white paper, so the palette was validated against #ffffff rather
# than a screen surface. Text never wears a series color; it wears these.
SURFACE = "#ffffff"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

# ── categorical palette ───────────────────────────────────────────────────────────
# Fixed order. Assigned in sequence, NEVER cycled — a 9th series folds into "Other",
# becomes small multiples, or the chart is the wrong form.
CATEGORICAL: tuple[str, ...] = (
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
)
MAX_SERIES = len(CATEGORICAL)

# Scatter / bubble / small-multiples put arbitrary pairs side by side, so they are
# validated on ALL pairs rather than adjacent ones — and only the first three slots
# clear that bar. The 4th puts yellow beside orange (normal-vision ΔE 13.7, below the
# 15 floor). This is a series cap, not a palette problem: fold to "Other" or facet.
MAX_SERIES_ALL_PAIRS = 3

# Secondary encoding, carried alongside hue on every series. Three jobs at once:
# grayscale print, full-severity CVD, and the contrast relief that slots 3/4/5 owe
# (they sit below 3:1 on white: aqua 2.82, yellow 2.17, magenta 2.69).
LINESTYLES: tuple[str, ...] = (
    "-",
    "--",
    "-.",
    ":",
    (0, (3, 1, 1, 1)),  # type: ignore[assignment]
    (0, (5, 1)),  # type: ignore[assignment]
    (0, (1, 1)),  # type: ignore[assignment]
    (0, (3, 1, 1, 1, 1, 1)),  # type: ignore[assignment]
)
MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v", "P", "X", "*")

# Markers key a line to the legend; they are not a per-sample annotation. Roughly this
# many per line keeps them readable on a dense sweep. See `series(n_points=...)`.
MARKERS_PER_LINE = 8

# ── sequential (continuous magnitude) ─────────────────────────────────────────────
# One hue, light→dark. Never a rainbow.
SEQUENTIAL_STEPS: tuple[str, ...] = (
    "#cde2fb",
    "#b7d3f6",
    "#9ec5f4",
    "#86b6ef",
    "#6da7ec",
    "#5598e7",
    "#3987e5",
    "#2a78d6",
    "#256abf",
    "#1c5cab",
    "#184f95",
    "#104281",
    "#0d366b",
)

# Discrete ordered marks (tiers, buckets) need visible gaps between steps, which the
# full ramp above does not have. Validated: monotone L, all adjacent ΔL >= 0.06,
# light end 2.11:1 on white, hue spread 3°.
ORDINAL_STEPS: tuple[str, ...] = ("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281")

# ── diverging (polarity about a baseline) ─────────────────────────────────────────
# Two hues + a NEUTRAL GRAY midpoint, equal steps per arm. A hue at the midpoint
# would read as a third category instead of "no difference".
DIVERGING_LOW = "#2a78d6"
DIVERGING_MID = "#f0efec"
DIVERGING_HIGH = "#e34948"

# ── status (reserved meaning — never "series 4") ──────────────────────────────────
# Always shipped with a label, never color alone.
STATUS: dict[str, str] = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# ── figure geometry ───────────────────────────────────────────────────────────────
# Two-column venue (IEEE/ACM) text widths, in inches.
WIDTH_1COL = 3.35
WIDTH_2COL = 7.16
DPI_RASTER = 600  # publication DPI for .png; .pdf is vector and unaffected


def rcparams() -> dict[str, Any]:
    """The rcParams this project's figures use. Recessive chrome, data-forward."""
    return {
        # Type: one sans everywhere, sized to stay legible at single-column width.
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "sans-serif"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.titlesize": 10,
        # Ink. Text tokens only — a series hue is never used for text.
        "text.color": INK_PRIMARY,
        "axes.labelcolor": INK_SECONDARY,
        "axes.titlecolor": INK_PRIMARY,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "xtick.labelcolor": INK_SECONDARY,
        "ytick.labelcolor": INK_SECONDARY,
        # Surfaces.
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        # Chrome: hairline, solid, recessive. Only the left and bottom spines survive;
        # a full box is ink that carries no data.
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",  # never dashed — dashes compete with the data
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        # Marks.
        "lines.linewidth": 1.8,
        "lines.markersize": 5,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.markeredgewidth": 1.2,
        "lines.markeredgecolor": SURFACE,  # the surface ring, so overlaps stay legible
        "patch.linewidth": 0,
        # Legend: present whenever there are >= 2 series, and never a heavy box.
        "legend.frameon": False,
        "legend.handlelength": 2.2,
        "legend.columnspacing": 1.2,
        "legend.labelspacing": 0.4,
        "legend.borderpad": 0.2,
        # Output.
        "figure.dpi": 150,
        "savefig.dpi": DPI_RASTER,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "savefig.transparent": False,
        "pdf.fonttype": 42,  # embed TrueType, not Type 3 — most venues require this
        "ps.fonttype": 42,
        # The categorical order, so a bare ax.plot() still lands on slot 1, 2, 3...
        "axes.prop_cycle": mpl.cycler(color=list(CATEGORICAL)),
    }


def use() -> None:
    """Apply the style globally. Prefer `figure()` or `style()`; this is for notebooks."""
    mpl.rcParams.update(rcparams())


@contextlib.contextmanager
def style() -> Iterator[None]:
    """Apply the style for the duration of a block, then restore the caller's rcParams."""
    with mpl.rc_context(rcparams()):
        yield


def series(index: int, *, all_pairs: bool = False, n_points: int | None = None) -> dict[str, Any]:
    """Everything that distinguishes series `index`: color plus its secondary encoding.

    Args:
        index: 0-based series number. Assigned in fixed order, never cycled.
        all_pairs: True for scatter/bubble/small-multiples, where any two marks can sit
            side by side and the series cap is 3 rather than 8.
        n_points: length of the series being plotted. Pass it for line charts — markers
            then thin out to roughly `MARKERS_PER_LINE` per line instead of one per
            sample. A marker on every point of a dense sweep merges into a solid band,
            hides the line it is meant to key, and erases the linestyle that carries
            identity in grayscale print. Omit only for genuinely sparse series.

    Raises:
        ValueError: past the cap. Cycling hues would silently reuse a color and make two
            different series look identical, so this refuses rather than wraps. Fold the
            extras into "Other", or facet into small multiples.
    """
    cap = MAX_SERIES_ALL_PAIRS if all_pairs else MAX_SERIES
    if not 0 <= index < cap:
        kind = "all-pairs (scatter/bubble/small-multiples)" if all_pairs else "adjacent"
        raise ValueError(
            f"series index {index} is outside the {kind} cap of {cap}. Hues are never "
            'cycled — fold the extra series into "Other" or facet into small multiples.'
        )
    spec: dict[str, Any] = {
        "color": CATEGORICAL[index],
        "linestyle": LINESTYLES[index],
        "marker": MARKERS[index],
    }
    if n_points is not None and n_points > MARKERS_PER_LINE:
        stride = max(2, round(n_points / MARKERS_PER_LINE))
        # Stagger the phase per series so markers from different lines interleave
        # instead of stacking on the same x positions where the lines cross.
        spec["markevery"] = (index % stride, stride)
    return spec


def sequential_cmap() -> LinearSegmentedColormap:
    """Continuous one-hue ramp for magnitude (heatmaps, density)."""
    return LinearSegmentedColormap.from_list("qsteg_sequential", list(SEQUENTIAL_STEPS))


def diverging_cmap() -> LinearSegmentedColormap:
    """Two hues around a neutral gray midpoint, for signed deviation from a baseline."""
    return LinearSegmentedColormap.from_list(
        "qsteg_diverging", [DIVERGING_LOW, DIVERGING_MID, DIVERGING_HIGH]
    )


@contextlib.contextmanager
def figure(
    width: float = WIDTH_1COL, height: float = 2.4, **kwargs: Any
) -> Iterator[tuple[Figure, Any]]:
    """A styled figure and axes. Closes the figure on exit, so long runs do not leak.

    `save()` must be called inside the block — the rcParams that govern output DPI and
    font embedding are only in effect here.
    """
    with style():
        fig, ax = plt.subplots(figsize=(width, height), **kwargs)
        try:
            yield fig, ax
        finally:
            plt.close(fig)


def finish(
    ax: Any,
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title: str | None = None,
    legend: bool | None = None,
) -> None:
    """Apply the labelling rules: grid behind the data, legend for >= 2 series.

    `legend=None` (the default) decides from the artist count — a single series gets no
    legend box, because the title already names what is plotted.
    """
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, loc="left", pad=8)
    ax.set_axisbelow(True)

    labelled = [h for h in ax.get_legend_handles_labels()[1] if not h.startswith("_")]
    if legend is None:
        legend = len(labelled) >= 2
    if legend and labelled:
        ax.legend()


def save(fig: Figure, path: str | Path, formats: tuple[str, ...] = ("pdf", "png")) -> list[Path]:
    """Write the figure once per format, creating parent directories as needed.

    `path` carries no extension — the formats supply it. PDF is the one that goes into
    LaTeX (vector, so it stays sharp at any print size); PNG is for quick review.
    """
    stem = Path(path)
    stem.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for fmt in formats:
        out = stem.with_suffix(f".{fmt}")
        fig.savefig(out, format=fmt)
        written.append(out)
    return written
