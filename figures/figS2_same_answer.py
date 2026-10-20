"""Supplementary Figure S2: the same-answer intervention.

Figure contract
- Claim: permuting timestamps within 2 km cells keeps every full-day answer set
  but changes the cost ordering of 277 of 279 windows, so record counts alone do
  not determine the ordering in the tested representation.
- (a) all 279 windows, D before and after the permutation.
- (b) the same windows near parity, where the seven sign changes sit.
- (c) the resource terms behind two sign changes, Beijing and Rome.
- (d) forward adjacent-scale crossings before and after the permutation.
Counts in (d) are those of the sealed M2 report (2,540 pairs with both ends
nonempty before and after; 19 crossings gained, 12 lost). The resource terms in
(c) are read directly from the sealed evidence archive (SR_EVIDENCE).
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd

import style as S

S.apply()
EVIDENCE = S.EVIDENCE
d = pd.read_csv(S.SOURCE / "figureS2_full_day_d.csv")
flips = pd.read_csv(EVIDENCE / "cities_multiscale_mechanism_20260921_v1/tables/same_membership_ordering_flips.csv")
to_q, to_c = d.to_quantum.astype(bool), d.to_classical.astype(bool)
assert len(d) == 279 and (d.D_original != d.D_shuffled).sum() == 277 and to_q.sum() == 4 and to_c.sum() == 3
beijing = flips[flips.source_id.eq("tdrive") & flips.k_old.eq(183286)].iloc[0]
rome = flips[flips.source_id.eq("rome_taxi") & flips.k_old.eq(46389)].iloc[0]
M2_FORWARD = dict(before=123, after=130, pairs=2540, gained=19, lost=12)

fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 128 * S.MM))
gs = fig.add_gridspec(2, 2, left=0.085, right=0.985, top=0.93, bottom=0.085, wspace=0.28, hspace=0.42)
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
rest = ~to_q & ~to_c


def scatter_d(ax, s_rest, s_flip):
    ax.scatter(d.D_original[rest], d.D_shuffled[rest], s=s_rest, color=S.STONE, linewidths=0, zorder=2)
    ax.scatter(d.D_original[to_q], d.D_shuffled[to_q], s=s_flip, color=S.SOFT_WARM, edgecolors=S.SOFT_WARM_TEXT,
               linewidths=0.6, zorder=3)
    ax.scatter(d.D_original[to_c], d.D_shuffled[to_c], s=s_flip, color=S.SOFT_CLASSICAL,
               edgecolors=S.SOFT_CLASSICAL_TEXT, linewidths=0.6, zorder=3)
    ax.axhline(0, color=S.GREY, lw=0.5, zorder=1)
    ax.axvline(0, color=S.GREY, lw=0.5, zorder=1)


# ---- (a) all windows -------------------------------------------------------
scatter_d(ax_a, 9, 24)
lim = (-8, 14.5)
ax_a.plot(lim, lim, color=S.MID_GREY, lw=0.5, ls=(0, (3, 2)), zorder=1)
ax_a.add_patch(Rectangle((-0.6, -0.6), 1.65, 1.65, fill=False, edgecolor=S.INK, lw=0.6, zorder=4))
ax_a.set_xlim(lim)
ax_a.set_ylim(lim)
S.log2_ratio_ticks(ax_a, "x", [-6, 0, 6, 12])
S.log2_ratio_ticks(ax_a, "y", [-6, 0, 6, 12])
ax_a.set_xlabel("Q/C, original timestamps")
ax_a.set_ylabel("Q/C, permuted timestamps")
ax_a.legend(handles=[
    Line2D([], [], ls="none", marker="o", ms=3.4, color=S.STONE, label=f"Same ordering ({rest.sum()})"),
    Line2D([], [], ls="none", marker="o", ms=3.8, markerfacecolor=S.SOFT_WARM, markeredgecolor=S.SOFT_WARM_TEXT,
           label=f"Turns quantum-cheaper ({to_q.sum()})"),
    Line2D([], [], ls="none", marker="o", ms=3.8, markerfacecolor=S.SOFT_CLASSICAL,
           markeredgecolor=S.SOFT_CLASSICAL_TEXT, label=f"Turns classical-cheaper ({to_c.sum()})")],
    loc="lower right", borderaxespad=0.3, handletextpad=0.3, labelspacing=0.4)

# ---- (b) near parity -------------------------------------------------------
scatter_d(ax_b, 14, 34)
ax_b.plot([-0.6, 1.05], [-0.6, 1.05], color=S.MID_GREY, lw=0.5, ls=(0, (3, 2)), zorder=1)
ax_b.set_xlim(-0.6, 1.05)
ax_b.set_ylim(-0.6, 1.05)
ax_b.set_xlabel("D = log₂(Q/C), original")
ax_b.set_ylabel("D = log₂(Q/C), permuted")

# ---- (c) resource terms of two sign changes --------------------------------
terms = [("M", "Candidates"), ("G", "Gates per attempt"), ("Q", "Quantum cost"), ("C", "Classical cost")]
x = np.arange(len(terms))
for off, row, color, name in [(-0.19, beijing, S.SOFT_TERRACOTTA, f"Beijing, K = {beijing.k_old:,}"),
                              (0.19, rome, S.SOFT_CLASSICAL, f"Rome, K = {rome.k_old:,}")]:
    vals = [np.log2(row[f"{t}_new"] / row[f"{t}_old"]) for t, _ in terms]
    ax_c.bar(x + off, vals, width=0.36, color=color, linewidth=0, label=name)
ax_c.axhline(0, color=S.INK, lw=0.6)
ax_c.set_xticks(x, [label for _, label in terms])
ax_c.set_ylabel("log₂(permuted / original)")
ax_c.legend(loc="lower right", handlelength=1.0)

# ---- (d) forward crossings before and after --------------------------------
f = M2_FORWARD
ax_d.bar([0, 1], [f["before"], f["after"]], width=0.55, color=[S.STONE, S.SOFT_WARM], linewidth=0)
for xi, v in zip([0, 1], [f["before"], f["after"]]):
    ax_d.text(xi, v + 3, f"{v}", ha="center", va="bottom", fontsize=6.5, color=S.INK, fontweight="bold")
ax_d.text(1, f["after"] / 2, f"+{f['gained']} new\n−{f['lost']} lost", ha="center", va="center", fontsize=6.3,
          color=S.INK, linespacing=1.3)
ax_d.set_xticks([0, 1], ["Original", "Permuted"])
ax_d.set_xlim(-0.6, 1.6)
ax_d.set_ylim(0, 160)
ax_d.set_ylabel(f"Forward crossings (of {f['pairs']:,} pairs)")

for ax, letter in zip([ax_a, ax_b, ax_c, ax_d], "abcd"):
    S.panel_label(ax, letter)
S.save(fig, "figureS2_same_answer")
