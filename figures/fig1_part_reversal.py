"""Figure 1 part: scale reversal of the two access costs (vector, schematic).

Cost against window size for classical-led preparation (C, teal) and quantum
filtering (Q, quantum colour). Q starts lower and rises faster, so the sign of
D = log2(Q/C) changes as the window grows: the pale warm band marks windows
where Q < C, the pale teal band windows where C < Q. Bars at one small and
one large window show the cheaper route at each end of a forward reversal.
Curves are schematic. Exported as editable SVG and a transparent 1,000 dpi PNG.
"""
from matplotlib.patches import FancyArrowPatch
import numpy as np

import fig1_parts_common as C
import style as S

SIZE_MM = (36.0, 36.6)
PALE_Q = "#F8D5DE"


def cost_c(x):
    return 0.30 + 0.42 * x


def cost_q(x):
    return 0.10 + 0.95 * x ** 1.5


def draw(ax):
    x = np.linspace(0.03, 1.0, 200)
    c, q = cost_c(x), cost_q(x)
    ax.fill_between(x, q, c, where=q <= c, color=PALE_Q, lw=0, interpolate=True, zorder=1)
    ax.fill_between(x, c, q, where=q >= c, color=S.PALE_CLASSICAL, lw=0, interpolate=True, zorder=1)
    ax.plot(x, c, color=S.CLASSICAL, lw=1.2, solid_capstyle="round", zorder=3)
    ax.plot(x, q, color=S.QUANTUM_DEEP, lw=1.2, solid_capstyle="round", zorder=3)
    cross = x[np.argmin(np.abs(q - c))]
    ax.scatter([cross], [cost_c(cross)], s=14, color="white", edgecolors=S.INK, linewidths=0.7, zorder=5)
    for xs, low, high, color in [(0.27, cost_q, cost_c, S.QUANTUM_DEEP), (0.88, cost_c, cost_q, S.CLASSICAL)]:
        ax.plot([xs, xs], [low(xs), high(xs)], color=color, lw=1.6, solid_capstyle="butt", zorder=4)
        ax.scatter([xs], [low(xs)], s=12, color=color, edgecolors="white", linewidths=0.5, zorder=5)
    ax.text(1.03, cost_c(1.0), "C", color=S.CLASSICAL_DEEP, fontsize=7, fontstyle="italic", ha="left",
            va="center")
    ax.text(1.03, cost_q(1.0), "Q", color=S.QUANTUM_DEEP, fontsize=7, fontstyle="italic", ha="left", va="center")
    for end in [(1.06, 0.0), (0.0, 1.1)]:
        ax.add_patch(FancyArrowPatch((0, 0), end, arrowstyle="-|>", mutation_scale=6, color=S.INK, lw=0.7,
                                     shrinkA=0, shrinkB=0, zorder=2))
    ax.text(0.5, -0.06, "Window size", color=S.INK, fontsize=6.5, ha="center", va="top")
    ax.text(-0.06, 0.55, "Cost", color=S.INK, fontsize=6.5, ha="right", va="center", rotation=90)
    ax.set_xlim(-0.16, 1.12)
    ax.set_ylim(-0.17, 1.13)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return {"crossing": round(float(cross), 3)}


if __name__ == "__main__":
    print("part10_scale_reversal", C.export(draw, "part10_scale_reversal", *SIZE_MM))
