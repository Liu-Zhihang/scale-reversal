"""Figure 1 part: the two access routes to one coherent output (vector).

After the shared index traversal the request forks. Classical-led preparation
(teal) reads the five leaf blocks the query reached, resolves membership and
then prepares the state; its cost is C. Quantum filtering (quantum colours)
is drawn as a circuit on three wires: candidate preparation over the
frontier, a controlled step, the geometric test, and postselection by
measurement, with the prepare-and-test loop repeated about M/K times; its cost
is Q. Both routes end in the same output |S1>. The circuit is schematic.
Exported as editable SVG and a transparent 1,000 dpi PNG.
"""
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch, Rectangle

import fig1_parts_common as C
import style as S

SIZE_MM = (44.0, 31.5)
XLIM, YLIM = (-0.02, 1.6), (-0.14, 1.02)
LANE_C, WIRES = 0.8, (0.12, 0.22, 0.32)
LIGHT_GATE, LIGHT_EDGE = "#FEC287", "#FB8861"


def arrow(ax, pts, color, lw=0.8):
    """Polyline whose last segment ends in an arrowhead."""
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, solid_joinstyle="miter", solid_capstyle="butt", zorder=2)
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=6, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=2))


def gate(ax, x, y0, y1, face, edge, w=0.07):
    ax.add_patch(FancyBboxPatch((x - w / 2, y0), w, y1 - y0, boxstyle="round,pad=0,rounding_size=0.012",
                                facecolor=face, edgecolor=edge, lw=0.6, zorder=4))


def meter(ax, x, y, w=0.075, h=0.075):
    """Measurement symbol: box, arc and needle."""
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, facecolor="white", edgecolor=S.INK, lw=0.6, zorder=4))
    ax.add_patch(Arc((x, y - h * 0.22), w * 0.7, h * 0.7, theta1=0, theta2=180, color=S.INK, lw=0.55, zorder=5))
    ax.plot([x, x + w * 0.25], [y - h * 0.22, y + h * 0.3], color=S.INK, lw=0.55, zorder=5)


def draw(ax):
    # ---- Fork after the shared index traversal ----------------------------------
    ax.plot([0, 0.05], [0.5, 0.5], color=S.INK, lw=0.8, zorder=2)
    ax.plot([0.05, 0.05], [WIRES[1], LANE_C], color=S.INK, lw=0.8, zorder=2)
    ax.plot([0.05, 0.1], [WIRES[1], WIRES[1]], color=S.INK, lw=0.8, zorder=2)

    # ---- Classical-led: read the reached blocks, then prepare ---------------------
    ax.text(0.1, 0.9, "Classical-led", color=S.CLASSICAL_DEEP, fontsize=6.5, ha="left", va="bottom")
    ax.plot([0.05, 1.2], [LANE_C, LANE_C], color=S.CLASSICAL, lw=0.8, zorder=2)
    for x in (0.2, 0.34, 0.48, 0.62, 0.76):
        ax.add_patch(FancyBboxPatch((x - 0.05, LANE_C - 0.05), 0.1, 0.1, boxstyle="round,pad=0,rounding_size=0.015",
                                    facecolor=S.CLASSICAL, edgecolor=S.CLASSICAL_DEEP, lw=0.6, zorder=3))
        for dy in (-0.024, 0.0, 0.024):
            ax.plot([x - 0.028, x + 0.028], [LANE_C + dy] * 2, color="white", lw=0.6, solid_capstyle="round",
                    zorder=4)
    ax.text(1.0, LANE_C + 0.05, "C", color=S.CLASSICAL_DEEP, fontsize=7, fontstyle="italic", ha="center",
            va="bottom")
    arrow(ax, [(1.2, LANE_C), (1.2, 0.56), (1.27, 0.56)], S.CLASSICAL)

    # ---- Quantum filtering: prepare candidates, test, postselect; repeat ~M/K ----
    for y in WIRES:
        ax.plot([0.1, 1.12], [y, y], color=S.GREY, lw=0.6, zorder=1)
    for x in (0.1, 1.12):
        ax.plot([x, x], [WIRES[0], WIRES[-1]], color=S.INK, lw=0.8, zorder=2)
    for y in WIRES:
        gate(ax, 0.2, y - 0.035, y + 0.035, LIGHT_GATE, LIGHT_EDGE, w=0.06)
    gate(ax, 0.33, WIRES[0] - 0.05, WIRES[-1] + 0.05, S.QUANTUM, S.QUANTUM_DEEP)
    ax.plot([0.46, 0.46], [WIRES[0], WIRES[-1]], color=S.INK, lw=0.6, zorder=3)
    ax.scatter([0.46], [WIRES[-1]], s=7, color=S.INK, edgecolors="none", zorder=5)
    gate(ax, 0.46, WIRES[0] - 0.035, WIRES[0] + 0.035, "#E0455F", S.QUANTUM_DEEP, w=0.06)
    gate(ax, 0.59, WIRES[0] - 0.05, WIRES[-1] + 0.05, S.QUANTUM_DEEP, "#7E2257")
    meter(ax, 0.73, WIRES[0])
    ax.add_patch(FancyArrowPatch((0.76, 0.41), (0.29, 0.41), connectionstyle="arc3,rad=0.38", arrowstyle="-|>",
                                 mutation_scale=6, color=S.QUANTUM_DEEP, lw=0.7, shrinkA=0, shrinkB=0, zorder=3))
    ax.text(0.525, 0.55, r"$\times\,M/K$", color=S.QUANTUM_DEEP, fontsize=6.5, ha="center", va="bottom")
    ax.text(1.0, WIRES[-1] + 0.05, "Q", color=S.QUANTUM_DEEP, fontsize=7, fontstyle="italic", ha="center",
            va="bottom")
    ax.text(0.1, 0.02, "Quantum filtering", color=S.QUANTUM_DEEP, fontsize=6.5, ha="left", va="top")
    arrow(ax, [(1.12, WIRES[1]), (1.2, WIRES[1]), (1.2, 0.44), (1.27, 0.44)], S.QUANTUM_DEEP)

    # ---- The shared output -------------------------------------------------------
    ax.add_patch(FancyBboxPatch((1.27, 0.36), 0.31, 0.28, boxstyle="round,pad=0,rounding_size=0.04",
                                facecolor="#FAFAF8", edgecolor=S.INK, lw=0.8, zorder=3))
    ax.text(1.425, 0.5, r"$|S_1\rangle$", color=S.INK, fontsize=9, ha="center", va="center", zorder=4)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.set_axis_off()


if __name__ == "__main__":
    C.export(draw, "part9_access_routes", *SIZE_MM)
    print("wrote part9_access_routes")
