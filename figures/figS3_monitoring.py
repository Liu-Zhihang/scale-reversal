"""Supplementary Figure S3: Jinan and Dublin monitoring contrasts.

Figure contract
- Claim: in the two earliest monitoring tasks, background support and access
  ordering change with window size, but forward crossings both improve and
  worsen reconstruction, and the same expansion can move error in opposite
  directions at different widths or dates.
- (a)/(d) support: windows per extent split into Q < C, other supported and
  empty, for Jinan (144 device hold-out targets) and Dublin (192 hour blocks).
- (b)/(e) direction: forward crossings with error up or down (Dublin also
  shows its reverse crossings).
- (c)/(f) dates: date-level change in mean absolute error for one expansion at
  two widths. Jinan keeps native PM units; Dublin is in ug/m3.
Jinan inputs and the Dublin pair table are read directly from the sealed
evidence archive (SR_EVIDENCE); the Dublin grid and daily tables are figure
source tables.
"""
import json

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import style as S

S.apply()
EVIDENCE = S.EVIDENCE

# ---- Jinan -----------------------------------------------------------------
je = pd.read_csv(EVIDENCE / "cities_jinan_e1_20260921_v1r1/tables/endpoints.csv")
je["supported"] = je.supported.astype(str).str.lower().isin(["true", "1"])
widths, durations = [500, 2000, 5000], [900, 3600, 21600]
jcells = []
for w in widths:
    for dur in durations:
        cell = je[je.width_m.eq(w) & je.duration_s.eq(dur)]
        sup = cell[cell.supported]
        jcells.append(dict(w=w, d=dur, lower=int((sup.Q < sup.C).sum()), supported=len(sup), total=len(cell)))
assert sum(c["lower"] for c in jcells) == 46 and all(c["total"] == 144 for c in jcells)
contrasts = json.loads((EVIDENCE / "cities_jinan_e1_20260921_v1r1/metrics/paired_contrasts.json").read_text())
jdays = {w: next(c for c in contrasts if c["axis"] == "time" and int(c["fixed_scale"]) == w and int(c["small"]) == 3600)
         for w in (2000, 5000)}
assert jdays[2000]["n_pairs"] == 127 and jdays[5000]["n_pairs"] == 143
J_UP, J_DOWN = 52, 39   # Table 2, Jinan monitoring forward pairs

# ---- Dublin ----------------------------------------------------------------
dg = pd.read_csv(S.SOURCE / "figureS3_dublin_grid.csv")
dd = pd.read_csv(S.SOURCE / "figureS3_dublin_daily.csv")
dp = pd.read_csv(EVIDENCE / "cities_dublin_e2_20260922_v1/tables/scale_pairs.csv")
both = dp[dp.status.eq("both_supported")]
flag = lambda s: s.astype(str).str.lower().isin(["true", "1"])
fwd, rev = both[flag(both.forward)], both[flag(both.reverse)]
assert len(fwd) == 61 and len(rev) == 19
d_down, d_up = int(fwd.error_direction.eq("down").sum()), int(fwd.error_direction.eq("up").sum())
assert (d_down, d_up) == (35, 26) and dg.lower.sum() == 69

# ---- Layout ----------------------------------------------------------------
fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 118 * S.MM))
gs = fig.add_gridspec(2, 3, left=0.075, right=0.985, top=0.92, bottom=0.1,
                      wspace=0.42, hspace=0.55)
axes = [[fig.add_subplot(gs[i, j]) for j in range(3)] for i in range(2)]


def support_bars(ax, cells, total, xlabels, group_labels=None, x=None):
    x = np.arange(len(cells)) if x is None else np.asarray(x)
    lower = np.array([c["lower"] for c in cells])
    sup = np.array([c["supported"] for c in cells])
    ax.bar(x, lower, width=0.72, color=S.SOFT_WARM, linewidth=0)
    ax.bar(x, sup - lower, bottom=lower, width=0.72, color=S.PALE_CLASSICAL, linewidth=0)
    ax.bar(x, total - sup, bottom=sup, width=0.72, color=S.SAND, linewidth=0)
    ax.set_xticks(x, xlabels)
    ax.set_ylim(0, total)
    ax.tick_params(axis="x", length=0)
    if group_labels:
        for gx, label in group_labels:
            ax.text(gx, -0.11, label, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6.5,
                    fontweight="bold")


def direction_bars(ax, items):
    for xi, (label, value, color) in enumerate(items):
        ax.bar(xi, value, width=0.62, color=color, linewidth=0)
        ax.text(xi, value + 1, f"{value}", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color=S.INK)
    ax.set_xticks(range(len(items)), [label for label, _, _ in items])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(items) - 0.4)


def date_dots(ax, groups, ylabel):
    for xi, (label, values) in enumerate(groups):
        values = np.asarray(values)
        colors = [S.SOFT_TERRACOTTA if v > 1e-12 else S.SOFT_CLASSICAL if v < -1e-12 else S.STONE for v in values]
        jitter = np.linspace(-0.12, 0.12, len(values))
        ax.scatter(xi + jitter, values, s=20, c=colors, edgecolors="white", linewidths=0.5, zorder=3)
        ax.plot(xi, values.mean(), marker="D", ms=4.2, color=S.INK, zorder=4)
    ax.axhline(0, color=S.GREY, lw=0.6)
    ax.set_xticks(range(len(groups)), [label for label, _ in groups])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylabel(ylabel)


# Jinan row
dur_label = {900: "15m", 3600: "1h", 21600: "6h"}
jx = [g * 3.6 + k for g in range(3) for k in range(3)]   # a gap separates the three widths
support_bars(axes[0][0], jcells, 144, [dur_label[c["d"]] for c in jcells],
             [(1, "0.5 km"), (4.6, "2 km"), (8.2, "5 km")], x=jx)
axes[0][0].set_ylabel("Jinan windows (of 144)")
direction_bars(axes[0][1], [("Error up", J_UP, S.SOFT_TERRACOTTA), ("Error down", J_DOWN, S.SOFT_CLASSICAL)])
axes[0][1].set_ylim(0, 70)
axes[0][1].set_ylabel("Forward crossings")
date_dots(axes[0][2], [(f"2 km\n{jdays[2000]['n_pairs']} targets", [v["delta_error"] for v in jdays[2000]["day_values"]]),
                       (f"5 km\n{jdays[5000]['n_pairs']} targets", [v["delta_error"] for v in jdays[5000]["day_values"]])],
          "MAE change, 1 h → 6 h\n(native PM units)")

# Dublin row
dcells = [dict(lower=r.lower, supported=r.supported) for r in dg.itertuples()]
support_bars(axes[1][0], dcells, 192, ["0.5 km", "2 km", "5 km"])
axes[1][0].set_ylabel("Dublin windows (of 192)")
direction_bars(axes[1][1], [("Error up", d_up, S.SOFT_TERRACOTTA), ("Error down", d_down, S.SOFT_CLASSICAL),
                            ("Reverse", len(rev), S.STONE)])
axes[1][1].set_ylim(0, 48)
axes[1][1].set_ylabel("Adjacent spatial pairs")
groups = {key: dd[(dd.small == key[0]) & (dd.large == key[1])].delta_error.tolist() for key in [(500, 2000), (2000, 5000)]}
date_dots(axes[1][2], [("0.5 → 2 km", groups[(500, 2000)]), ("2 → 5 km", groups[(2000, 5000)])],
          "MAE change (µg/m³)")

axes[0][0].legend(handles=[Patch(color=S.SOFT_WARM, label="Q < C"), Patch(color=S.PALE_CLASSICAL, label="Other supported"),
                           Patch(color=S.SAND, label="Empty")],
                  loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, borderaxespad=0.2, handlelength=1.0,
                  columnspacing=1.0)
for ax, letter in zip([a for row in axes for a in row], "abcdef"):
    S.panel_label(ax, letter, dx_pt=-30)
S.save(fig, "figureS3_monitoring")
