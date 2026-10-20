"""Figure 3: enlarging a physical window can reverse the access-cost ordering.

Figure contract
- Claim: in 1,060 of 17,592 adjacent-scale pairs, classical-led preparation is
  cheaper at the smaller window and quantum filtering at the larger one. The
  reversals arise from widening and from lengthening, occur in 11 of 13 cities,
  and coexist with a majority of windows that stay classical-led.
- (a) context: share of nonempty, fully supported windows with Q < C on the
  width x duration grid.
- (b) hero: every adjacent pair placed by Q/C at its smaller and larger window;
  forward reversals occupy the lower-right quadrant.
- (c) magnitude: Q/C of the forward pairs before and after expansion, split by
  the expanded axis.
- (d) generality: forward pairs as a share of adjacent pairs, by source, keeping
  the Paris and Barcelona zeros.

All 13,370 windows and 17,592 pairs are drawn. The counts asserted below are the
ones reported in the manuscript; the figure is not written if any differs.
"""
import re

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize, TwoSlopeNorm
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

import style as S

S.apply()
rng = np.random.default_rng(20261020)

# ---- Data and manuscript checks --------------------------------------------
grid = pd.read_csv(S.SOURCE / "figure2_extent_grid.csv")
pairs = pd.read_csv(S.SOURCE / "figure2_pairs.csv.gz")
sources = pd.read_csv(S.SOURCE / "figure2_sources.csv")

width_of = lambda q: int(re.search(r"_w(\d+)", q).group(1))
pairs["axis"] = np.where(
    [width_of(s) != width_of(l) for s, l in zip(pairs.small_query, pairs.large_query)],
    "width", "duration")
forward = pairs[pairs.direction.eq("forward")]
reverse = pairs[pairs.direction.eq("reverse")]
others = pairs[~pairs.direction.eq("forward")]
x, y = pairs.small_D, pairs.large_D
quadrant = {
    "forward": int(((x > 0) & (y < 0)).sum()), "reverse": int(((x < 0) & (y > 0)).sum()),
    "classical": int(((x > 0) & (y > 0)).sum()), "quantum": int(((x < 0) & (y < 0)).sum()),
}
assert grid.n.sum() == 13370 and grid.lower.sum() == 742
assert len(pairs) == 17592 and len(forward) == 1060 and len(reverse) == 11
assert quadrant["forward"] == 1060 and quadrant["reverse"] == 11
assert round(2 ** forward.small_D.median(), 1) == 3.9 and round(2 ** forward.large_D.median(), 2) == 0.46
cities_positive = {S.SOURCE_CITY[s] for s in sources.loc[sources.forward > 0, "source_id"]}
assert len(cities_positive) == 11 and len(set(S.SOURCE_CITY.values())) == 13

# ---- Layout ----------------------------------------------------------------
fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 140 * S.MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 0.92],
                      left=0.09, right=0.985, top=0.905, bottom=0.075, wspace=0.18, hspace=0.32)
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

# ---- (a) where on the width x duration grid --------------------------------
widths, durations = [250, 500, 1000, 2000, 5000, 10000], [900, 3600, 21600, 86400]
k = grid.pivot(index="duration_s", columns="width_m", values="lower").reindex(index=durations, columns=widths).to_numpy()
n = grid.pivot(index="duration_s", columns="width_m", values="n").reindex(index=durations, columns=widths).to_numpy()
share = 100 * k / n
im = ax_a.imshow(share, cmap=S.WARM_SEQ, vmin=0, vmax=50, origin="lower", aspect="auto")
for i in range(len(durations)):
    for j in range(len(widths)):
        ax_a.text(j, i, f"{k[i, j]}/{n[i, j]:,}", ha="center", va="center", fontsize=6.2,
                  color="white" if share[i, j] > 24 else S.INK)
ax_a.set_xticks(np.arange(-0.5, 6), minor=True)
ax_a.set_yticks(np.arange(-0.5, 4), minor=True)
ax_a.grid(which="minor", color="white", lw=1.2)
ax_a.tick_params(which="both", length=0)
ax_a.set_xticks(range(6), ["0.25", "0.5", "1", "2", "5", "10"])
ax_a.set_yticks(range(4), ["15 min", "1 h", "6 h", "24 h"])
for side in ax_a.spines.values():
    side.set_visible(False)
ax_a.set_xlabel("Full square width (km)")
ax_a.set_ylabel("Centred duration")

# ---- (b) every adjacent pair in the cost-ordering plane --------------------
lim_x, lim_y = (-7.2, 13.6), (-7.8, 13.6)
density = LogNorm(1, 1000)
ax_b.add_patch(Rectangle((0, lim_y[0]), lim_x[1], -lim_y[0], facecolor=S.PALE_WARM, edgecolor="none", zorder=0))
hex_kw = dict(gridsize=(42, 36), extent=(*lim_x, *lim_y), mincnt=1, norm=density, linewidths=0)
hb_other = ax_b.hexbin(others.small_D, others.large_D, cmap=S.CLASSICAL_SEQ, zorder=1, **hex_kw)
hb_fwd = ax_b.hexbin(forward.small_D, forward.large_D, cmap=S.WARM_STRONG, zorder=2, **hex_kw)
ax_b.plot(lim_x, lim_x, color=S.MID_GREY, lw=0.5, ls=(0, (3, 2)), zorder=3)
ax_b.axvline(0, color=S.GREY, lw=0.6, zorder=3)
ax_b.axhline(0, color=S.GREY, lw=0.6, zorder=3)
ax_b.scatter(reverse.small_D, reverse.large_D, s=9, color=S.INK, edgecolors="white", linewidths=0.4, zorder=4)
ax_b.set_xlim(lim_x)
ax_b.set_ylim(lim_y)
S.log2_ratio_ticks(ax_b, "x", [-6, -3, 0, 3, 6, 9, 12])
S.log2_ratio_ticks(ax_b, "y", [-6, -3, 0, 3, 6, 9, 12])
ax_b.set_xlabel("Q/C at the smaller window")
ax_b.set_ylabel("Q/C at the larger window")
quad_text = [
    (13.2, -7.3, "right", "bottom", "Forward reversal", f"{quadrant['forward']:,} pairs", S.QUANTUM_DEEP, "bold"),
    (-6.8, 13.2, "left", "top", "Reverse crossing", f"{quadrant['reverse']} pairs", S.INK, "normal"),
    (0.5, 13.2, "left", "top", "Classical-led at both", f"{quadrant['classical']:,} pairs", S.CLASSICAL, "normal"),
    (-7.05, -0.7, "left", "top", "Quantum at both", f"{quadrant['quantum']} pairs", S.GREY, "normal"),
]
for qx, qy, ha, va, head, count, color, weight in quad_text:
    halo = dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85)
    ax_b.text(qx, qy, f"{head}\n{count}", ha=ha, va=va, fontsize=6.5, color=color, fontweight=weight,
              linespacing=1.25, zorder=5, bbox=halo if head.startswith("Quantum") else None)

# ---- (c) how far the forward pairs move ------------------------------------
ratio_norm = TwoSlopeNorm(vcenter=0, vmin=-6.5, vmax=6.5)
rows = [("width", "Widened"), ("duration", "Lengthened")]
for row, (axis, label) in enumerate(rows):
    sub = forward[forward.axis.eq(axis)]
    base = len(rows) - 1 - row
    for offset, values in [(0.17, sub.small_D), (-0.17, sub.large_D)]:
        jitter = rng.uniform(-0.085, 0.085, len(values))
        ax_c.scatter(values, base + offset + jitter, s=1.6, c=values, cmap=S.DIVERGING,
                     norm=ratio_norm, alpha=0.85, linewidths=0, zorder=2)
        ax_c.plot([np.median(values)] * 2, [base + offset - 0.13, base + offset + 0.13],
                  color=S.INK, lw=1.1, solid_capstyle="butt", zorder=4)
    m_small, m_large = np.median(sub.small_D), np.median(sub.large_D)
    ax_c.annotate("", xy=(m_large, base), xytext=(m_small, base),
                  arrowprops=dict(arrowstyle="-|>", color=S.INK, lw=0.7, mutation_scale=6), zorder=5)
    ax_c.text(m_small, base + 0.34, f"{2 ** m_small:.1f}", ha="center", va="bottom", fontsize=6.3, color=S.CLASSICAL)
    ax_c.text(m_large, base - 0.34, f"{2 ** m_large:.2f}", ha="center", va="top", fontsize=6.3, color=S.QUANTUM_DEEP)
ax_c.text(-0.3, 1.17, "Smaller window", ha="right", va="center", fontsize=6.3, color=S.CLASSICAL)
ax_c.text(0.3, 0.83, "Larger window", ha="left", va="center", fontsize=6.3, color=S.QUANTUM_DEEP)
ax_c.axvline(0, color=S.GREY, lw=0.6, ls=(0, (3, 2)), zorder=1)
ax_c.text(0.15, -0.6, "Q = C", ha="left", va="bottom", fontsize=6.3, color=S.GREY)
ax_c.set_xlim(-6.8, 6.8)
ax_c.set_ylim(-0.62, 1.62)
S.log2_ratio_ticks(ax_c, "x", [-6, -4, -2, 0, 2, 4, 6])
counts = forward.axis.value_counts()
ax_c.set_yticks([1, 0], [f"Widened\nn = {counts['width']}", f"Lengthened\nn = {counts['duration']}"])
ax_c.tick_params(axis="y", length=0)
ax_c.spines["left"].set_visible(False)
ax_c.set_xlabel("Q/C of forward-reversal pairs")

# ---- (d) forward share by source -------------------------------------------
src = sources.assign(share=100 * sources.forward / sources.n).sort_values(["share", "n"], ascending=[False, False])
yy = np.arange(len(src))
positive = (src.forward > 0).to_numpy()
ax_d.hlines(yy, 0, src.share, color=S.LIGHT_GREY, lw=0.8, zorder=1)
ax_d.scatter(src.share[positive], yy[positive], s=15, c=src.share[positive], cmap=S.WARM_STRONG,
             norm=Normalize(0, 15), linewidths=0, zorder=3)
ax_d.scatter(src.share[~positive], yy[~positive], s=15, facecolors="white", edgecolors=S.GREY,
             linewidths=0.7, zorder=3)
for yi, (_, r) in zip(yy, src.iterrows()):
    ax_d.text(r.share + 0.7, yi, f"{S.SOURCE_LABEL[r.source_id]}  {r.forward}/{r.n:,}", va="center",
              fontsize=6.3, color=S.INK if r.forward else S.GREY)
ax_d.set_ylim(len(src) - 0.4, -0.6)
ax_d.set_xlim(0, 30)
ax_d.set_xticks([0, 5, 10, 15])
ax_d.spines["bottom"].set_bounds(0, 15)
ax_d.set_yticks([])
ax_d.spines["left"].set_color(S.MID_GREY)
ax_d.set_xlabel("Forward reversals (% of adjacent pairs)")

# ---- Colour keys and panel letters -----------------------------------------
keys = S.stacked_keys(fig, ax_a, [im], ["Windows with Q < C (%)"], [0, 25, 50], ["0", "25", "50"])
keys += S.stacked_keys(fig, ax_b, [hb_other, hb_fwd], ["Other pairs per bin", "Forward reversals per bin"],
                       [1, 10, 100, 1000], ["1", "10", "100", "1,000"], frac=0.34)
for ax, letter in zip([ax_a, ax_b, ax_c, ax_d], "abcd"):
    S.panel_label(ax, letter)

S.save(fig, "figure3_reversal", exclude_axes=keys)
