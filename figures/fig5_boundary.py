"""Figure 6: one resource boundary, and where cities meet it.

Figure contract
- Claim: every window's ordering follows one break-even rule. Quantum filtering
  wins once enough records accumulate with pure, cheap attempts, until classical
  whole-block acceptance closes the region; forward reversals differ from other
  expansions by accumulation and by index consolidation. Favourable windows
  concentrate where supported observations are dense, but not at the reference
  centre in every city.
- (a) hero: all 13,370 windows in the plane of records K against purity per
  attempt cost, with the approximate large-window reference line.
- (b) mechanism: standardized change in ln Psi for forward reversals and for
  expansions that stay classical-led, split into its three exact components.
- (c) support: central/side/corner shares under three denominators.
- (d) heterogeneity: the same shares by source.

Inputs are sealed derived tables: the figure source tables and, for (b), the
decomposition strata read directly from the sealed evidence archive
(SR_EVIDENCE). Every count asserted below is reported in the manuscript; the
figure is not written if any differs.
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import style as S

S.apply()
EVIDENCE = S.EVIDENCE

# ---- Data and manuscript checks --------------------------------------------
phase = pd.read_csv(S.SOURCE / "figure4_phase.csv.gz")
rings = pd.read_csv(S.SOURCE / "figure4_geography.csv").set_index("ring")
anchors = pd.read_csv(S.SOURCE / "figure2_anchor_counts.csv")
strata = pd.read_csv(EVIDENCE / "cities_breakeven_geography_20260923_v1/tables/decomposition_strata.csv")

phase["lower"] = phase.Q < phase.C
lx = np.log10(phase.k)
ly = np.log10(phase.k / phase.M / phase.trial_cost)
ref = 1 / 4.43
above = (lx + ly) > np.log10(ref)
block = ~phase.lower & phase.c_route.eq("C_BLOCK")
other = ~phase.lower & ~block
assert len(phase) == 13370 and phase.lower.sum() == 742
assert (phase.lower & ~above).sum() == 13 and (~phase.lower & above).sum() == 113
assert (block & above).sum() == 109 and (phase.C <= phase.prefix).sum() == 979
assert round(float(np.median(phase.C[phase.k >= 20000] / phase.k[phase.k >= 20000])), 2) == 4.43

w = strata.n_forward / strata.n_forward.sum()
parts = ["dK", "dpi", "dH"]
fwd = {p: float((w * strata[f"forward_{p}"]).sum()) for p in parts}
stay = {p: float((w * strata[f"nocross_{p}"]).sum()) for p in parts}
gap = sum(fwd.values()) - sum(stay.values())
share = {p: (fwd[p] - stay[p]) / gap for p in parts}
assert round(sum(fwd.values()), 2) == 2.60 and round(sum(stay.values()), 2) == 0.83
assert round(share["dK"], 2) == 0.44 and round(share["dpi"] + share["dH"], 2) == 0.56
assert tuple(rings.loc[["center", "side", "corner"], "favorable"]) == (307, 302, 133)

# ---- Layout ----------------------------------------------------------------
fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 140 * S.MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 0.95],
                      left=0.085, right=0.985, top=0.93, bottom=0.075, wspace=0.2, hspace=0.36)
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

# ---- (a) the resource plane ------------------------------------------------
for mask, color, size in [(other, "#BFD6D7", 1.4), (block, S.CLASSICAL, 2.6), (phase.lower, S.QUANTUM, 2.6)]:
    ax_a.scatter(lx[mask], ly[mask], s=size, color=color, linewidths=0, zorder=2)
xlim, ylim = (-0.15, 6.3), (-7.7, -3.85)
xx = np.linspace(*xlim, 200)
yy = np.log10(ref) - xx
keep = (yy > ylim[0]) & (yy < ylim[1])
ax_a.plot(xx[keep], yy[keep], color=S.INK, lw=0.8, zorder=3)
ax_a.text(5.98, -6.5, "Ψ*", ha="left", va="bottom", fontsize=7, color=S.INK)
ax_a.set_xlim(xlim)
ax_a.set_ylim(ylim)
ax_a.set_xticks(range(7), ["1", "10", "100", "1k", "10k", "100k", "1M"])
ax_a.set_yticks([-7, -6, -5, -4])
ax_a.set_xlabel("Records in the window, K")
ax_a.set_ylabel("log₁₀(candidate purity / attempt cost)")
ax_a.legend(handles=[
    Line2D([], [], ls="none", marker="o", ms=3, color=S.QUANTUM, label="Quantum cheaper"),
    Line2D([], [], ls="none", marker="o", ms=3, color=S.CLASSICAL, label="Whole-block classical"),
    Line2D([], [], ls="none", marker="o", ms=3, color="#BFD6D7", label="Other classical")],
    loc="lower right", borderaxespad=0.3, handletextpad=0.2, labelspacing=0.35)

# ---- (b) what separates forward reversals ----------------------------------
labels = {"dK": "Records", "dpi": "Purity", "dH": "Attempt cost"}
colors = {"dK": "#F4D3BC", "dpi": "#E4A9AE", "dH": "#9DC3C5"}   # light apricot, dusty rose, light teal
rows = [("Forward\nreversals", fwd), ("Stayed\nclassical-led", stay)]
for yi, (_, comp) in enumerate(rows):
    pos, neg = 0.0, 0.0
    for p in parts:
        v = comp[p]
        left = pos if v >= 0 else neg + v
        ax_b.barh(yi, v if v >= 0 else -v, left=left, height=0.5, color=colors[p], linewidth=0)
        if v >= 0:
            pos += v
        else:
            neg += v
    total = sum(comp.values())
    ax_b.text(pos + 0.06, yi, f"{total:.2f}", ha="left", va="center", fontsize=6.5, color=S.INK, fontweight="bold")
ax_b.axvline(0, color=S.INK, lw=0.6)
ax_b.set_yticks([0, 1], [r[0] for r in rows])
ax_b.set_ylim(1.75, -0.55)
ax_b.tick_params(axis="y", length=0)
ax_b.spines["left"].set_visible(False)
ax_b.set_xlim(-0.35, 3.1)
ax_b.set_xticks([0, 1, 2, 3])
ax_b.spines["bottom"].set_bounds(0, 3)
ax_b.set_xlabel("Standardized change in ln Ψ")
ax_b.text(3.05, 1.62, f"Gap {gap:.2f}: records {share['dK']:.0%}, purity {share['dpi']:.0%},\n"
          f"attempt cost {share['dH']:.0%}", ha="right", va="bottom", fontsize=6.3, color=S.GREY,
          linespacing=1.25)
ax_b.legend(handles=[Patch(color=colors[p], label=labels[p]) for p in parts], loc="lower right",
            bbox_to_anchor=(1.0, 1.0), ncol=3, borderaxespad=0.2, handlelength=1.0, columnspacing=1.0)

# ---- (c) the anchor gradient under three denominators ----------------------
dens = [("registered", "Registered"), ("supported", "Fully\nsupported"), ("nonempty", "Nonempty,\nsupported")]
# (fill, text) pairs: light marks with deeper text so labels stay legible.
ring_style = [("center", "Central", ("#D58BA4", "#9E3F63")), ("side", "Side, 6.7 km", ("#EFA48C", "#B4553A")),
              ("corner", "Corner, 9.4 km", ("#F3C99B", "#A3612A"))]
xs = np.arange(len(dens))
for ring, name, (fill, text) in ring_style:
    vals = [100 * rings.loc[ring, "favorable"] / rings.loc[ring, col] for col, _ in dens]
    ax_c.plot(xs, vals, color=fill, lw=1.6, marker="o", ms=4.5, markeredgecolor=text, markeredgewidth=0.5, zorder=3)
    for xi, v in zip(xs, vals):
        ax_c.text(xi, v * 1.16, f"{v:.1f}", ha="center", va="bottom", fontsize=6.2, color=text)
    ax_c.text(xs[-1] + 0.12, vals[-1], name, ha="left", va="center", fontsize=6.5, color=text)
ratio = [rings.loc["center", "favorable"] / rings.loc["center", c] /
         (rings.loc["corner", "favorable"] / rings.loc["corner", c]) for c, _ in dens]
ax_c.text(0.02, 0.97, f"Central / corner ratio {ratio[0]:.1f}× → {ratio[-1]:.1f}×", transform=ax_c.transAxes,
          ha="left", va="top", fontsize=6.3, color=S.GREY)
ax_c.set_yscale("log")
ax_c.set_ylim(0.3, 20)
ax_c.set_yticks([0.5, 1, 2, 5, 10], ["0.5", "1", "2", "5", "10"])
ax_c.yaxis.set_minor_locator(plt.NullLocator())
ax_c.set_xticks(xs, [d[1] for d in dens])
ax_c.set_xlim(-0.3, 2.95)
ax_c.set_ylabel("Windows with Q < C (%)")
ax_c.set_xlabel("Denominator")

# ---- (d) the same gradient by source ---------------------------------------
by = anchors.groupby(["source_id", "ring"])[["lower", "nonempty_supported"]].sum()
pct = (100 * by.lower / by.nonempty_supported).unstack()
pct = pct.reindex(columns=["center", "side", "corner"])
peripheral_first = pct[["side", "corner"]].max(axis=1) > pct["center"]
order = pct.assign(m=pct.max(axis=1)).sort_values(["m", "center"], ascending=False).index.tolist()
ys = np.arange(len(order))
for yi, sid in zip(ys, order):
    vals = pct.loc[sid].dropna()
    ax_d.hlines(yi, vals.min(), vals.max(), color=S.LIGHT_GREY, lw=1.6, zorder=1)
    zero = vals.max() == 0
    for ring, _, (fill, text) in ring_style:
        if ring in vals:
            ax_d.scatter(vals[ring], yi, s=16, zorder=3, linewidths=0.7 if zero else 0.5,
                         facecolors="white" if zero else fill, edgecolors=S.GREY if zero else text)
    ax_d.text(vals.max() + 0.7, yi, S.SOURCE_LABEL[sid], va="center", fontsize=6.3,
              color=S.GREY if zero else S.INK, fontweight="bold" if peripheral_first[sid] else "normal")
ax_d.axvline(0, color=S.LIGHT_GREY, lw=0.6, zorder=0)
ax_d.set_ylim(len(order) - 0.4, -0.6)
ax_d.set_xlim(-0.6, 32)
ax_d.set_xticks([0, 5, 10, 15, 20])
ax_d.spines["bottom"].set_bounds(0, 20)
ax_d.set_yticks([])
ax_d.spines["left"].set_visible(False)
ax_d.set_xlabel("Windows with Q < C (% of nonempty, supported)")
ax_d.legend(handles=[Line2D([], [], ls="none", marker="o", ms=3.6, markerfacecolor=f, markeredgecolor=tc,
                            markeredgewidth=0.5, label=n.split(",")[0]) for _, n, (f, tc) in ring_style],
            loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, borderaxespad=0.2, handletextpad=0.2,
            columnspacing=0.9)

for ax, letter in zip([ax_a, ax_b, ax_c, ax_d], "abcd"):
    S.panel_label(ax, letter)

S.save(fig, "figure6_boundary_geography")
