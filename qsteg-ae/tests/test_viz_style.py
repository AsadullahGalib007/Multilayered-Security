"""Guards on the single figure style.

The palette was validated once with the data-viz validator (protanopia/deuteranopia
separation, normal-vision floor, lightness band, chroma floor, contrast on white paper)
and the numbers recorded in `docs/decisions/003-figure-style.md`. These tests do not
re-derive that color science — they pin the exact hexes and the structural rules the
validation assumed, so an edit that would invalidate the recorded result fails here
instead of silently shipping into the paper.
"""

from __future__ import annotations

import matplotlib
import pytest

matplotlib.use("Agg")

from src.viz import style  # noqa: E402  — backend must be set before pyplot is imported

# The exact validated set, in the validated order. The ORDER is the colorblind-safety
# mechanism: re-ordering changes which pairs are adjacent and invalidates the run.
VALIDATED_CATEGORICAL = (
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#4a3aa7",
    "#e34948",
)


def test_categorical_palette_matches_the_validated_set() -> None:
    assert style.CATEGORICAL == VALIDATED_CATEGORICAL, (
        "the categorical palette changed — re-run the data-viz validator on both the "
        "adjacent and all-pairs lists and update docs/decisions/003-figure-style.md"
    )


def test_palette_has_no_duplicate_slots() -> None:
    assert len(set(style.CATEGORICAL)) == len(style.CATEGORICAL)


def test_every_series_has_a_distinct_secondary_encoding() -> None:
    """Hue alone must never carry identity: grayscale print and CVD both need this."""
    assert len(set(style.LINESTYLES)) == style.MAX_SERIES
    assert len(set(style.MARKERS)) == style.MAX_SERIES


def test_series_assigns_slots_in_fixed_order() -> None:
    for i in range(style.MAX_SERIES):
        assert style.series(i)["color"] == style.CATEGORICAL[i]


def test_series_refuses_to_cycle_hues() -> None:
    """A 9th series must fail loudly, not silently reuse slot 1."""
    with pytest.raises(ValueError, match="never"):
        style.series(style.MAX_SERIES)
    with pytest.raises(ValueError):
        style.series(-1)


def test_all_pairs_forms_cap_at_three_series() -> None:
    """Scatter/bubble/small-multiples: the 4th slot fails the normal-vision floor."""
    assert style.MAX_SERIES_ALL_PAIRS == 3
    style.series(2, all_pairs=True)
    with pytest.raises(ValueError, match="all-pairs"):
        style.series(3, all_pairs=True)


def test_markers_thin_out_on_dense_series() -> None:
    """One marker per sample merges into a band and hides the line it keys."""
    assert "markevery" not in style.series(0)
    assert "markevery" not in style.series(0, n_points=style.MARKERS_PER_LINE)

    spec = style.series(0, n_points=600)
    offset, stride = spec["markevery"]
    assert stride == pytest.approx(600 / style.MARKERS_PER_LINE, abs=1)
    assert offset == 0

    # Different series stagger their phase so markers interleave at crossings.
    assert style.series(1, n_points=600)["markevery"][0] != offset


def test_colormaps_build_and_are_not_rainbows() -> None:
    sequential = style.sequential_cmap()
    diverging = style.diverging_cmap()
    assert sequential.name == "qsteg_sequential"
    assert diverging.name == "qsteg_diverging"

    # Sequential must be monotone in luminance; that is what makes it read as magnitude.
    def luminance(rgba: tuple[float, ...]) -> float:
        return 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]

    lums = [luminance(sequential(i / 10)) for i in range(11)]
    assert lums == sorted(lums, reverse=True), "sequential ramp is not monotone light→dark"

    # Diverging must pass through a near-neutral midpoint, never a third hue.
    r, g, b, _ = diverging(0.5)
    assert max(r, g, b) - min(r, g, b) < 0.05, "diverging midpoint is not neutral"


def test_rcparams_keep_chrome_recessive() -> None:
    params = style.rcparams()
    assert params["axes.spines.top"] is False
    assert params["axes.spines.right"] is False
    assert params["grid.linestyle"] == "-", "dashed gridlines compete with the data"
    assert params["pdf.fonttype"] == 42, "most venues reject Type 3 fonts"
    assert params["savefig.dpi"] == style.DPI_RASTER


def test_style_context_restores_caller_rcparams() -> None:
    before = matplotlib.rcParams["lines.linewidth"]
    with style.style():
        assert matplotlib.rcParams["lines.linewidth"] == 1.8
    assert matplotlib.rcParams["lines.linewidth"] == before


def test_finish_adds_a_legend_only_for_multiple_series(tmp_path) -> None:
    with style.figure() as (_fig, ax):
        ax.plot([0, 1], [0, 1], label="only one")
        style.finish(ax, xlabel="x", ylabel="y")
        assert ax.get_legend() is None, "a single series needs no legend box"

    with style.figure() as (_fig, ax):
        ax.plot([0, 1], [0, 1], label="first", **style.series(0))
        ax.plot([0, 1], [1, 0], label="second", **style.series(1))
        style.finish(ax, xlabel="x", ylabel="y")
        assert ax.get_legend() is not None


def test_save_writes_every_requested_format(tmp_path) -> None:
    with style.figure() as (fig, ax):
        ax.plot([0, 1], [0, 1])
        written = style.save(fig, tmp_path / "nested" / "fig")

    assert [p.suffix for p in written] == [".pdf", ".png"]
    assert all(p.is_file() and p.stat().st_size > 0 for p in written)
