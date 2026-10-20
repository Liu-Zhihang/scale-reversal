"""Figure 4: lower operation prices move the reversals but do not remove them.

Figure contract
- Claim: across all 45 lookup and quantum-geometry price combinations, forward
  reversals persist (1,060 to 1,377 pairs) while the median window stays
  classical-led (median Q/C above 15). Lower prices change which pairs reverse
  and spread reversals to all 13 cities.
- (a) persistence: forward reversals at every combination.
- (b) limit: median Q/C at every combination.
- (c) turnover: forward pairs retained from, added to and lost from the L1 set
  at the four registered reporting points.
- (d) location: forward share by source at the reporting points, including the
  Paris and Barcelona pairs that appear only at lower prices.

Every combination and every source is drawn. The values asserted below are the
ones reported in Table 2 and Section 3.2.
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd

import style as S

S.apply()

# ---- Data and manuscript checks --------------------------------------------
grid = pd.read_csv(S.SOURCE / "figure3_prices.csv")
by_source = pd.read_csv(S.SOURCE / "figure3_sources.csv")
lookups = [100, 30, 10, 3, 1]
geometries = [10000, 3000, 1000, 300, 100, 30, 10, 3, 1]
report = [(100, 10000), (10, 1000), (1, 100), (1, 1)]
g = grid.set_index(["lookup", "quantum_geometry"])
assert len(grid) == 45 and grid.forward_pairs.min() == 1060 and grid.forward_pairs.max() == 1377
assert grid.q_over_c_median.min() > 15
expected = {  # lower windows, median Q/C, forward, reverse, cities
    (100, 10000): (742, 33.13, 1060, 11, 11), (10, 1000): (1253, 19.29, 1348, 28, 13),
    (1, 100): (1514, 16.89, 1368, 46, 13), (1, 1): (1559, 16.60, 1357, 49, 13)}
for key, (low, med, fwd, rev, cities) in expected.items():
    r = g.loc[key]
    assert (r.lower_windows, round(r.q_over_c_median, 2), r.forward_pairs, r.reverse_pairs,
            r.cities_with_forward) == (low, med, fwd, rev, cities), key
assert tuple(g.loc[(1, 1), ["forward_retained", "forward_added", "forward_lost"]]) == (907, 450, 153)
unit = by_source.set_index(["lookup", "quantum_geometry", "source_id"]).forward_pairs
assert unit[(1, 1, "paris_mat")] == 14 and unit[(1, 1, "barcelona")] == 6

# ---- Layout ----------------------------------------------------------------
fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 135 * S.MM))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], left=0.105, right=0.985, top=0.9, bottom=0.08,
                      wspace=0.2, hspace=0.42)
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])


def price_heatmap(ax, values, cmap, vmin, vmax, fmt, white_above):
    """Annotated lookup x geometry grid with the four reporting points outlined."""
    im = ax.imshow(values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    for i in range(len(lookups)):
        for j in range(len(geometries)):
            ax.text(j, i, fmt(values[i, j]), ha="center", va="center", fontsize=6.2,
                    color="white" if values[i, j] > white_above else S.INK)
    for lk, qg in report:
        i, j = lookups.index(lk), geometries.index(qg)
        ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=S.INK, lw=1.0, zorder=4))
    ax.set_xticks(np.arange(-0.5, len(geometries)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(lookups)), minor=True)
    ax.grid(which="minor", color="white", lw=1.0)
    ax.tick_params(which="both", length=0)
    ax.set_xticks(range(len(geometries)), ["10k", "3k", "1k", "300", "100", "30", "10", "3", "1"])
    ax.set_yticks(range(len(lookups)), [str(v) for v in lookups])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlabel("Quantum geometry price")
    return im


def matrix(column):
    return g[column].unstack().reindex(index=lookups, columns=geometries).to_numpy()


# ---- (a) persistence and (b) limit -----------------------------------------
im_a = price_heatmap(ax_a, matrix("forward_pairs"), S.WARM_SEQ, 1000, 1400, lambda v: f"{v:,.0f}", 1290)
ax_a.set_ylabel("Coherent lookup price")
im_b = price_heatmap(ax_b, matrix("q_over_c_median"), S.CLASSICAL_SEQ, 14, 36, lambda v: f"{v:.1f}", 25)

# ---- (c) turnover of forward pairs relative to the L1 set ------------------
labels = ["100 / 10,000\n(L1)", "10 / 1,000", "1 / 100", "1 / 1"]
yy = np.arange(len(report))
kept = np.array([g.loc[k, "forward_retained"] for k in report])
added = np.array([g.loc[k, "forward_added"] for k in report])
lost = np.array([g.loc[k, "forward_lost"] for k in report])
h = 0.56
ax_c.barh(yy, kept, height=h, color=S.QUANTUM_DEEP, linewidth=0)
ax_c.barh(yy, added, left=kept, height=h, color="#FEC287", linewidth=0)
ax_c.barh(yy, -lost, height=h, color=S.SOFT_CLASSICAL, linewidth=0)
for yi, k_, a_, l_ in zip(yy, kept, added, lost):
    ax_c.text(k_ / 2, yi, f"{k_:,}", ha="center", va="center", fontsize=6.2, color="white")
    if a_:
        ax_c.text(k_ + a_ / 2, yi, f"+{a_:,}", ha="center", va="center", fontsize=6.2, color=S.INK)
        ax_c.text(-l_ - 25, yi, f"−{l_:,}", ha="right", va="center", fontsize=6.2, color=S.CLASSICAL)
    ax_c.text(k_ + a_ + 25, yi, f"{k_ + a_:,}", ha="left", va="center", fontsize=6.3, color=S.INK,
              fontweight="bold")
ax_c.axvline(0, color=S.INK, lw=0.6)
ax_c.set_yticks(yy, labels)
ax_c.set_ylim(len(report) - 0.45, -0.55)
ax_c.set_xlim(-470, 1650)
ax_c.set_xticks([0, 500, 1000, 1500], ["0", "500", "1,000", "1,500"])
ax_c.spines["bottom"].set_bounds(0, 1500)
ax_c.spines["left"].set_visible(False)
ax_c.tick_params(axis="y", length=0)
ax_c.set_ylabel("Lookup / quantum geometry price")
ax_c.set_xlabel("Forward-reversal pairs")
ax_c.legend(handles=[Patch(color=S.QUANTUM_DEEP, label="Retained from L1"),
                     Patch(color="#FEC287", label="New"),
                     Patch(color=S.SOFT_CLASSICAL, label="Lost from L1")],
            loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, borderaxespad=0.2,
            handlelength=1.0, columnspacing=1.0)

# ---- (d) where reversals occur, by source ----------------------------------
point_colors = [S.CLASSICAL_DEEP, S.CLASSICAL_MID, S.QUANTUM_DEEP, "#FDA761"]
share = by_source.assign(share=100 * by_source.forward_pairs / by_source.eligible_pairs)
wide = share.pivot_table(index="source_id", columns=["lookup", "quantum_geometry"], values="share")
l1 = share[(share.lookup == 100) & (share.quantum_geometry == 10000)].set_index("source_id")
order = l1.sort_values(["share", "eligible_pairs"], ascending=[False, False]).index.tolist()
ys = np.arange(len(order))
for yi, sid in zip(ys, order):
    vals = [wide.loc[sid, k] for k in report]
    ax_d.hlines(yi, min(vals), max(vals), color=S.LIGHT_GREY, lw=1.6, zorder=1)
    ax_d.text(max(vals) + 0.8, yi, S.SOURCE_LABEL[sid], va="center", fontsize=6.3, color=S.INK)
for k, color in zip(report, point_colors):
    ax_d.scatter([wide.loc[s, k] for s in order], ys, s=13, color=color, linewidths=0, zorder=3)
ax_d.axvline(0, color=S.LIGHT_GREY, lw=0.6, zorder=0)
ax_d.set_ylim(len(order) - 0.4, -0.6)
ax_d.set_xlim(-0.8, 46)
ax_d.set_xticks([0, 10, 20, 30])
ax_d.spines["bottom"].set_bounds(0, 30)
ax_d.set_yticks([])
ax_d.spines["left"].set_visible(False)
ax_d.set_xlabel("Forward reversals (% of adjacent pairs)")
ax_d.legend(handles=[Line2D([], [], ls="none", marker="o", ms=3.4, color=c, label=l.replace("\n(L1)", ""))
                     for c, l in zip(point_colors, labels)],
            loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=4, borderaxespad=0.2,
            handletextpad=0.2, columnspacing=0.9)

# ---- Colour keys and panel letters -----------------------------------------
keys = S.stacked_keys(fig, ax_a, [im_a], ["Forward-reversal pairs"], [1000, 1200, 1400],
                      ["1,000", "1,200", "1,400"])
keys += S.stacked_keys(fig, ax_b, [im_b], ["Median Q/C"], [15, 25, 35], ["15", "25", "35"])
for ax, letter in zip([ax_a, ax_b, ax_c, ax_d], "abcd"):
    S.panel_label(ax, letter)

S.save(fig, "figure4_prices", exclude_axes=keys)
