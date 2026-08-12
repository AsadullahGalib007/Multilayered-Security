# 003 — Figure style and the validated palette

**Status:** accepted · **Phase:** P0.2 · **Date:** 2026-08-12

## Context

`CLAUDE.md` requires one style file, `src/viz/style.py`, used by every figure. P6.3
requires figures regenerated "at publication DPI … consistent style, colorblind-safe,
legible at print size." Colorblind-safety is a measurable property, so it was measured
rather than eyeballed — this file records the measurement so it can be re-checked when
someone is tempted to change a color.

## The palette

Eight categorical hues **in a fixed order**. The order is the safety mechanism, not
decoration: the checks below are run on *adjacent* pairs, so re-ordering changes which
pairs are tested and invalidates this record.

| Slot | Hue | Hex | | Slot | Hue | Hex |
|---|---|---|---|---|---|---|
| 1 | blue | `#2a78d6` | | 5 | magenta | `#e87ba4` |
| 2 | orange | `#eb6834` | | 6 | green | `#008300` |
| 3 | aqua | `#1baf7a` | | 7 | violet | `#4a3aa7` |
| 4 | yellow | `#eda100` | | 8 | red | `#e34948` |

Sequential (magnitude): one blue hue, 13 steps, light→dark. Diverging (polarity):
blue ↔ red about a **neutral gray** midpoint `#f0efec` — a hue at the midpoint would
read as a third category rather than "no difference". Status colors are reserved and
never used for a series.

## Validation

Run against **`#ffffff`**, not a screen surface: these figures print on paper. ΔE is
Euclidean distance in OKLab ×100; CVD is simulated with Machado–Oliveira–Fernandes
(2009) at severity 1.0.

**Categorical, adjacent pairs** (lines, bars, stacks) — all eight slots:

```
[PASS] Lightness band       all 8 inside L 0.43–0.77
[PASS] Chroma floor         all 8 >= 0.1
[PASS] CVD separation       worst adjacent #eda100↔#1baf7a ΔE 9.1 (protan) · tritan 5.8
[PASS] Normal-vision floor  worst adjacent #e87ba4↔#eda100 ΔE 19.6 (normal)
[WARN] Contrast vs surface  below 3:1: aqua 2.82, yellow 2.17, magenta 2.69
```

The contrast WARN is **not dismissable** — it obliges a relief channel. Satisfied by
`series()` shipping a distinct linestyle and marker with every hue, so identity never
rests on color alone.

**Categorical, all pairs** (scatter, bubble, small multiples) — where any two marks can
end up adjacent, so every pair is tested:

| slots | result |
|---|---|
| first 3 | **PASS** — worst pair CVD ΔE 9.2, normal-vision 24.0 |
| first 4 | **FAIL** — `#eda100`↔`#eb6834` normal-vision ΔE 13.7, below the 15 floor |

Hence `MAX_SERIES_ALL_PAIRS = 3`. This is a **series cap, not a palette defect**: no
re-ordering fixes it, because the all-pairs list does not depend on order. A scatter
needing a 4th series folds it into "Other" or facets into small multiples.

**Ordinal ramp** (discrete ordered marks). The first attempt — consecutive steps from
the sequential ramp — **failed**: `#2a78d6`↔`#256abf` had ΔL 0.048, below the 0.06
floor, so the steps would not have read as distinct tiers. Re-stepped to 100-spacing:

```
[PASS] Lightness monotone / Adjacent ΔL / Light-end contrast 2.11:1 / Single hue 3°
```

## Decisions beyond color

- **Markers thin to ~8 per line** (`MARKERS_PER_LINE`), staggered per series. Caught by
  rendering the template and looking at it: a marker on all 60 points merged into a
  solid band and buried both the line and its linestyle. The validator cannot catch
  this — only looking at the output can.
- **`series()` raises past the cap** rather than cycling hues. A cycled palette silently
  paints two different series the same color, which is a wrong figure, not a style nit.
- **`pdf.fonttype = 42`** — Type 3 fonts are rejected by most venue submission systems.
- **PDF + PNG on every save.** PDF is what goes into LaTeX (vector, sharp at any size);
  PNG at 600 dpi is for quick review.
- **Text never wears a series color.** Axis and label text use ink tokens; identity
  comes from the colored mark beside the text. The light hues are illegible as text.

## Consequences

- `tests/test_viz_style.py` pins the exact hexes and the structural rules. It does not
  re-derive the color science — changing a hex fails the test, which sends you back
  here to re-run the validator.
- The validator itself is not vendored into this repo (it ships with the tooling that
  produced this record, and needs Node or its Python twin). Re-running it is a manual
  step at palette-change time, not a CI step.
- **Dual-axis charts are forbidden** and cannot be mechanically enforced. Two measures
  on different scales → two charts, small multiples, or index to a common base.
