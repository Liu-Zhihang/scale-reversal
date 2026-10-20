"""Figure 1 parts: the evaluation checklist card and the risk sign (vector, no text).

part11_checklist: a card with nine ticked rows, one per item of Table 4,
coloured by theme: task, background and local support (teal), output and
classical competitors (grey), prices and reuse (quantum colours), extent grid
and negative results (purple). Row bars are placeholders for the item text.
part12_risk: a vermilion warning triangle for the risk of choosing a
background because it lowers access cost.
Exported as editable SVG and transparent 1,000 dpi PNG.
"""
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

import fig1_parts_common as C
import style as S

CHECK_MM = (26.0, 34.0)
RISK_MM = (7.0, 6.4)
ROWS = [(S.CLASSICAL_DEEP, 0.30), (S.CLASSICAL, 0.36), (S.CLASSICAL_MID, 0.26), (S.GREY, 0.33), (S.GREY, 0.28),
        (S.QUANTUM, 0.24), (S.QUANTUM_DEEP, 0.34), ("#6A1C81", 0.29), ("#6A1C81", 0.37)]


def draw_checklist(ax):
    ax.add_patch(FancyBboxPatch((0.07, 0.02), 0.9, 1.24, boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor="#E8E8E5", edgecolor="none", zorder=0))
    ax.add_patch(FancyBboxPatch((0.04, 0.05), 0.9, 1.24, boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor="white", edgecolor=S.MID_GREY, lw=0.6, zorder=1))
    for i, (color, length) in enumerate(ROWS):
        y = 1.16 - i * 0.13
        ax.plot([0.13, 0.62], [y, y], color=color, alpha=0.28, lw=2.0, solid_capstyle="round", zorder=2)
        ax.plot([0.13, 0.13 + length], [y, y], color=color, lw=2.0, solid_capstyle="round", zorder=3)
        ax.add_patch(Circle((0.79, y), 0.045, facecolor="white", edgecolor=S.GREY, lw=0.6, zorder=3))
        ax.plot([0.765, 0.785, 0.815], [y, y - 0.022, y + 0.024], color=S.INK, lw=0.7, solid_joinstyle="miter",
                zorder=4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.31)
    ax.set_aspect("equal")
    ax.set_axis_off()


def draw_risk(ax):
    ax.add_patch(Polygon([(0, 0), (1, 0), (0.5, 0.87)], closed=True, facecolor="white", edgecolor=S.RISK, lw=1.0,
                         joinstyle="round", zorder=1))
    ax.plot([0.5, 0.5], [0.32, 0.6], color=S.RISK, lw=1.1, solid_capstyle="round", zorder=2)
    ax.scatter([0.5], [0.17], s=2.6, color=S.RISK, edgecolors="none", zorder=2)
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 0.97)
    ax.set_aspect("equal")
    ax.set_axis_off()


if __name__ == "__main__":
    C.export(draw_checklist, "part11_checklist", *CHECK_MM)
    C.export(draw_risk, "part12_risk", *RISK_MM)
    print("wrote part11_checklist, part12_risk")
