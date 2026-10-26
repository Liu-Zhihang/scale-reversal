"""Figure 4: crossing into lower access cost does not identify better backgrounds.

Figure contract
- Claim: for observed-speed reconstruction, crossings and standardized
  noncrossing expansions worsen error at almost the same rate; for mobile
  monitoring, crossings worsen it more often, with Dublin in the opposite
  direction. Neither task family supports choosing a background because it
  became cheaper to access.
- (a) rates: worsening rate of forward crossings beside the standardized
  noncrossing control, by source and pooled within each task family.
- (b) contrast: their difference with 95% date-block intervals against the
  prespecified five-point decision band.

Sources follow Table 2. Sources without forward crossings stay visible. The
pooled values asserted below are the ones reported in Section 3.2.
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import style as S

S.apply()

src = pd.read_csv(S.SOURCE / "figure5_sources.csv")
fam = pd.read_csv(S.SOURCE / "figure5_families.csv").set_index("family")
assert round(100 * fam.loc["speed", "forward_worse_rate"], 2) == 56.36
assert round(100 * fam.loc["speed", "standardised_control_worse_rate"], 2) == 56.35
assert round(100 * fam.loc["monitoring", "delta"], 2) == 15.72
assert (round(100 * fam.loc["monitoring", "delta_ci_low"], 2), round(100 * fam.loc["monitoring", "delta_ci_high"], 2)) == (1.31, 28.29)
assert fam.used_forward_n.sum() == 1484

NAMES = {**S.SOURCE_LABEL, "zurich": "Zurich", "portici": "Portici"}
groups = [
    ("speed", "Observed speed",
     ["tdrive", "jinan", "rio", "sf_cabspotting", "rome_taxi", "stellenbosch", "montreal", "barcelona", "brighton_shl"]),
    ("monitoring", "Mobile monitoring", ["jinan", "dublin", "zurich", "portici"]),
]
decided = {"CROSSING_WORSE", "CROSSING_BETTER"}

# Row plan: header, sources, pooled row; a small gap between families.
rows, y = [], 0.0
for family, title, order in groups:
    rows.append(dict(kind="header", y=y, label=title))
    y += 1
    table = src[src.family.eq(family)].set_index("source")
    for sid in order:
        r = table.loc[sid]
        rows.append(dict(kind="source", y=y, label=f"{NAMES[sid]}   {r.forward_n} · {r.forward_days}/{r.registered_days}", r=r))
        y += 1
    r = fam.loc[family]
    rows.append(dict(kind="pooled", y=y, label=f"Pooled   {r.used_forward_n:,}", r=r))
    y += 1.5
y_max = y - 1.5

fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 118 * S.MM))
gs = fig.add_gridspec(1, 2, left=0.215, right=0.985, top=0.9, bottom=0.1, wspace=0.12)
ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])

ax_b.axvspan(-5, 5, color="#F0EEEA", zorder=0, lw=0)
ax_b.axvline(0, color=S.MID_GREY, lw=0.6, zorder=1)
ax_a.axvline(50, color=S.LIGHT_GREY, lw=0.6, zorder=0)
CONTROL, CONTROL_DEEP = S.CLASSICAL_MID, S.CLASSICAL_DEEP

for row in rows:
    yi = row["y"]
    if row["kind"] == "header":
        continue
    r = row["r"]
    pooled = row["kind"] == "pooled"
    ms = 4.6 if pooled else 3.4
    if not r.used_forward_n:
        ax_a.text(2, yi, "No forward crossing", va="center", fontsize=6.3, color=S.GREY)
        continue
    for key, lo, hi, off, color, marker in [
            ("forward_worse_rate", "forward_ci_low", "forward_ci_high", -0.17,
             S.QUANTUM_DEEP if pooled else S.QUANTUM, "o"),
            ("standardised_control_worse_rate", "control_ci_low", "control_ci_high", 0.17,
             CONTROL_DEEP if pooled else CONTROL, "s")]:
        v, l, h = 100 * r[key], 100 * r[lo], 100 * r[hi]
        ax_a.plot([l, h], [yi + off] * 2, color=color, lw=1.1 if pooled else 0.8, solid_capstyle="butt", zorder=2)
        ax_a.plot(v, yi + off, marker=marker, ms=ms, color=color, ls="none", zorder=3)
    d, dl, dh = 100 * r.delta, 100 * r.delta_ci_low, 100 * r.delta_ci_high
    filled = r.operational_label in decided
    ax_b.plot([dl, dh], [yi, yi], color=S.INK, lw=1.1 if pooled else 0.8, solid_capstyle="butt", zorder=2)
    ax_b.plot(d, yi, marker="D" if pooled else "o", ms=ms, ls="none", zorder=3,
              markerfacecolor=S.INK if filled else "white", markeredgecolor=S.INK, markeredgewidth=0.8)
    if pooled:
        ax_b.text(dh + 1.5, yi, f"{d:+.2f} pp", va="center", fontsize=6.3, color=S.INK, fontweight="bold")

ticks = [row["y"] for row in rows]
for ax in (ax_a, ax_b):
    ax.set_ylim(y_max + 0.6, -0.6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    gap_y = next(row["y"] for row in rows if row["kind"] == "header" and row["y"] > 0) - 0.75
    ax.axhline(gap_y, color=S.LIGHT_GREY, lw=0.6)
ax_a.set_yticks(ticks, [row["label"] for row in rows])
for tick, row in zip(ax_a.get_yticklabels(), rows):
    if row["kind"] == "header":
        tick.set_fontweight("bold")
        tick.set_fontsize(7)
    elif row["kind"] == "pooled":
        tick.set_fontweight("bold")
ax_b.set_yticks(ticks, [""] * len(ticks))

ax_a.set_xlim(0, 100)
ax_a.set_xticks([0, 25, 50, 75, 100])
ax_a.set_xlabel("Expansions with worse reconstruction error (%)")
ax_b.set_xlim(-32, 66)
ax_b.set_xticks([-25, 0, 25, 50])
ax_b.spines["bottom"].set_bounds(-25, 60)
ax_b.set_xlabel("Crossing − standardized control (percentage points)")

ax_a.legend(handles=[Line2D([], [], marker="o", ms=3.4, color=S.QUANTUM, lw=0.8, label="Forward crossing"),
                     Line2D([], [], marker="s", ms=3.4, color=CONTROL, lw=0.8, label="Standardized noncrossing")],
            loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, borderaxespad=0.2, columnspacing=1.0)
ax_b.legend(handles=[Line2D([], [], marker="o", ms=3.4, ls="none", color=S.INK, label="Threshold met"),
                     Line2D([], [], marker="o", ms=3.4, ls="none", markerfacecolor="white", markeredgecolor=S.INK,
                            label="No information"),
                     Patch(color="#F0EEEA", label="±5 pp")],
            loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, borderaxespad=0.2, columnspacing=0.9,
            handletextpad=0.3, handlelength=1.0)

S.panel_label(ax_a, "a", dx_pt=-112)
S.panel_label(ax_b, "b", dx_pt=-12)

S.save(fig, "figure4_tasks")
